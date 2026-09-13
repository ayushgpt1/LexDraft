import { useState, useCallback } from 'react';
import { AlertCircle, FileText, Loader2, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Header } from '@/components/Header';
import { ReferenceDocuments } from '@/components/ReferenceDocuments';
import { FileUploadCard } from '@/components/FileUploadCard';
import { ProcessingPipeline } from '@/components/ProcessingPipeline';
import { CaseInformation } from '@/components/CaseInformation';
import { AffidavitPreview } from '@/components/AffidavitPreview';
import { EvaluationSummary } from '@/components/EvaluationSummary';
import { EvaluationCriteria, type NamedCriterion } from '@/components/EvaluationCriteria';
import { DeterministicChecks } from '@/components/DeterministicChecks';
import { IssuesSection } from '@/components/IssuesSection';
import { WorkflowExplanation } from '@/components/WorkflowExplanation';
import type {
  GenerateResponse,
  Issue,
  PipelineStage,
  ProgressEvent,
  StageStatus,
  UploadedFile,
} from '@/lib/types';
import {
  PIPELINE_STAGES,
  closeProgressSocket,
  connectProgressSocket,
  generateAffidavit,
  downloadDocx,
  loadPreloadedReferenceFile,
} from '@/lib/api';

type AppState = 'idle' | 'processing' | 'complete';

// Order of the stages exactly as the backend emits them over the
// /ws/progress socket (see backend/core/orchestrator.py).
const PROGRESS_STAGE_INDEXES: Record<string, number> = {
  extraction: 0,
  mapping: 1,
  generation: 2,
  validation: 3,
  evaluation: 4,
};

function buildCriteria(
  report: GenerateResponse['evaluation_report']
): NamedCriterion[] {
  return [
    { name: 'Entity Accuracy', criterion: report.entity_accuracy },
    { name: 'Completeness', criterion: report.completeness },
    { name: 'Semantic Faithfulness', criterion: report.semantic_faithfulness },
    { name: 'Hallucination', criterion: report.hallucination },
    { name: 'Template Fidelity', criterion: report.template_fidelity },
  ];
}

function buildIssues(response: GenerateResponse): Issue[] {
  const issues: Issue[] = [];

  // Failed deterministic checks
  response.validation_results
    .filter((check) => !check.passed)
    .forEach((check) =>
      check.issues.forEach((message) =>
        issues.push({
          source: 'deterministic',
          message: `${check.check}: ${message}`,
        })
      )
    );

  // Per-criterion LLM issues
  buildCriteria(response.evaluation_report).forEach(({ name, criterion }) =>
    criterion.issues.forEach((message) =>
      issues.push({ source: 'llm', message: `${name}: ${message}` })
    )
  );

  // Overall LLM issues
  response.evaluation_report.overall_issues.forEach((message) =>
    issues.push({ source: 'llm', message })
  );

  return issues;
}

function App() {
  const [caseFile, setCaseFile] = useState<File | null>(null);
  const [appState, setAppState] = useState<AppState>('idle');
  const [stages, setStages] = useState<PipelineStage[]>([]);
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedFormatFile, setSelectedFormatFile] = useState<File | null>(null);
  const [selectedSampleFile, setSelectedSampleFile] = useState<File | null>(null);

  const isProcessing = appState === 'processing';
  const canGenerate = caseFile !== null && !isProcessing;

  const toUploadedFile = (file: File | null): UploadedFile =>
    file ? { name: file.name, size: file.size } : null;

  const clearError = useCallback(() => setError(null), []);

  // Apply a backend progress event to the pipeline stages. Only the
  // reported stage is updated; previously completed stages stay
  // Complete and later stages are never marked Complete early.
  const applyProgressEvent = useCallback((event: ProgressEvent) => {
    const index = PROGRESS_STAGE_INDEXES[event.stage];
    if (index === undefined) return;

    setStages((prev) =>
      prev.map((stage, stageIndex) => {
        if (stageIndex !== index) return stage;

        if (event.status === 'processing') {
          return { ...stage, status: 'processing' as StageStatus };
        }
        if (event.status === 'complete') {
          return { ...stage, status: 'completed' as StageStatus };
        }
        if (event.status === 'error') {
          return { ...stage, status: 'error' as StageStatus };
        }
        return stage;
      })
    );
  }, []);

  const handleGenerate = useCallback(async () => {
    if (!caseFile || appState === 'processing') return;
    clearError();
    setResult(null);

    const runId = window.crypto.randomUUID();

    // Initial state: every stage is Waiting. Real backend events then
    // drive the transition to Processing/Complete.
    setStages(
      PIPELINE_STAGES.map((label, index) => ({
        id: `stage-${index}`,
        label,
        status: 'pending' as StageStatus,
      }))
    );
    setAppState('processing');

    let progressSocket: WebSocket | null = null;
    let socketErrorMessage: string | null = null;

    // Connect the progress WebSocket BEFORE the generation request so
    // no backend stage event is missed. Progress reporting is
    // optional: if the socket cannot be opened, generation still runs.
    try {
      const progress = connectProgressSocket(runId, (event) => {
        applyProgressEvent(event);
        if (event.status === 'error' && event.message) {
          socketErrorMessage = event.message;
        }
      });
      await progress.ready;
      progressSocket = progress.socket;
    } catch {
      progressSocket = null;
    }

    try {
      // POST /generate supports configurable reference materials:
      // - format_file (optional): custom Format Explained PDF
      // - sample_file (optional): custom Sample Affidavit PDF
      // - case_file (required): Case Information PDF
      // If format_file or sample_file are omitted, the default bundled
      // reference documents are used automatically.
      const response = await generateAffidavit(
        caseFile,
        selectedFormatFile || undefined,
        selectedSampleFile || undefined,
        runId
      );
      setResult(response);
      setStages((prev) =>
        prev.map((stage) => ({ ...stage, status: 'completed' as const }))
      );
      setAppState('complete');
    } catch (err) {
      // Keep the failed stage visible as Error; later stages are never
      // marked Complete. The existing final error banner still shows.
      setAppState('idle');
      setError(
        socketErrorMessage ??
          (err instanceof Error
            ? err.message
            : 'Affidavit generation failed. Please try again.')
      );
    } finally {
      closeProgressSocket(progressSocket);
    }
  }, [caseFile, appState, clearError, applyProgressEvent]);

  const handleDownload = useCallback(async () => {
    clearError();
    try {
      await downloadDocx();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Download failed. Please try again.'
      );
    }
  }, [clearError]);

  const handleInvalidFile = useCallback((fileName: string) => {
    setError(
      `"${fileName}" is not a PDF file. Please upload a valid PDF document.`
    );
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="mx-auto max-w-5xl px-6 py-8 space-y-8">
        {/* Input Section */}
        <section>
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-foreground">
              Create Affidavit in Reply
            </h2>
          </div>

          {error && (
            <Alert variant="destructive" className="mb-4">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Something went wrong</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-4">
            <ReferenceDocuments
              formatFile={selectedFormatFile}
              sampleFile={selectedSampleFile}
              onFormatChange={setSelectedFormatFile}
              onSampleChange={setSelectedSampleFile}
            />

            <FileUploadCard
              title="Case Information"
              description="Upload the case information PDF"
              uploadLabel="Upload Case Information PDF"
              file={toUploadedFile(caseFile)}
              disabled={isProcessing}
              onFileSelected={(f) => {
                clearError();
                setCaseFile(f);
              }}
              onInvalidFile={handleInvalidFile}
            />
          </div>

          <div className="flex justify-center mt-6">
            <Button
              size="lg"
              onClick={handleGenerate}
              disabled={!canGenerate}
              className="gap-2 min-w-[220px]"
            >
              {isProcessing ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Sparkles className="h-4 w-4" />
              )}
              {isProcessing ? 'Generating Affidavit…' : 'Generate Affidavit'}
            </Button>
          </div>

          {!canGenerate && appState === 'idle' && (
            <p className="text-center text-xs text-muted-foreground mt-3">
              Upload the Case Information PDF to enable generation — default
              reference materials are used unless you replace them above
            </p>
          )}
        </section>

        {/* Processing Pipeline */}
        {stages.length > 0 && (
          <section>
            <ProcessingPipeline stages={stages} />
          </section>
        )}

        {/* Results */}
        {appState === 'complete' && result && (
          <>
            <section>
              <CaseInformation data={result.case_data} />
            </section>

            <section>
              <AffidavitPreview
                caseData={result.case_data}
                paragraphs={result.generated_paragraphs.paragraphs}
                onDownload={handleDownload}
              />
            </section>

            <section>
              <h2 className="text-xl font-semibold text-foreground mb-4">
                Evaluation
              </h2>
              <div className="space-y-4">
                <EvaluationSummary
                  report={result.evaluation_report}
                  deterministic={result.deterministic_score}
                />
                <EvaluationCriteria
                  criteria={buildCriteria(result.evaluation_report)}
                />
              </div>
            </section>

            <section>
              <DeterministicChecks
                checks={result.validation_results}
                score={result.deterministic_score}
              />
            </section>

            <section>
              <IssuesSection issues={buildIssues(result)} />
            </section>
          </>
        )}

        {/* Workflow Explanation */}
        <WorkflowExplanation />

        {/* Footer */}
        <footer className="pt-8 pb-4 border-t border-border">
          <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
            <FileText className="h-3.5 w-3.5" />
            <span>LexDraft — AI-powered Legal Affidavit Agent</span>
          </div>
        </footer>
      </main>
    </div>
  );
}

export default App;

