import { useState, useCallback, useRef } from 'react';
import { FileText, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Header } from '@/components/Header';
import { ReferenceFormatStatus } from '@/components/ReferenceFormatStatus';
import { CaseInformationUpload } from '@/components/CaseInformationUpload';
import { ProcessingPipeline } from '@/components/ProcessingPipeline';
import { CaseInformation } from '@/components/CaseInformation';
import { AffidavitPreview } from '@/components/AffidavitPreview';
import { EvaluationSummary } from '@/components/EvaluationSummary';
import { EvaluationCriteria } from '@/components/EvaluationCriteria';
import { DeterministicChecks } from '@/components/DeterministicChecks';
import { IssuesSection } from '@/components/IssuesSection';
import { WorkflowExplanation } from '@/components/WorkflowExplanation';
import type {
  UploadedFile,
  PipelineStage,
  AffidavitResult,
} from '@/lib/types';
import {
  PIPELINE_STAGES,
  STAGE_DURATION_MS,
  getAffidavitResult,
  downloadDocx,
} from '@/lib/api';

type AppState = 'idle' | 'processing' | 'complete';

function App() {
  const [caseFile, setCaseFile] = useState<UploadedFile>(null);
  const [appState, setAppState] = useState<AppState>('idle');
  const [stages, setStages] = useState<PipelineStage[]>([]);
  const [result, setResult] = useState<AffidavitResult | null>(null);
  const timersRef = useRef<ReturnType<typeof setTimeout>[]>([]);

  const canGenerate = caseFile !== null && appState !== 'processing';

  const clearTimers = () => {
    timersRef.current.forEach(clearTimeout);
    timersRef.current = [];
  };

  const handleGenerate = useCallback(() => {
    if (!canGenerate) return;
    clearTimers();

    const initialStages: PipelineStage[] = PIPELINE_STAGES.map((label, i) => ({
      id: `stage-${i}`,
      label,
      status: 'pending' as const,
    }));

    setStages(initialStages);
    setResult(null);
    setAppState('processing');

    PIPELINE_STAGES.forEach((_, index) => {
      const startDelay = index * STAGE_DURATION_MS;
      const endDelay = startDelay + STAGE_DURATION_MS;

      const startTimer = setTimeout(() => {
        setStages((prev) =>
          prev.map((s, i) =>
            i === index ? { ...s, status: 'processing' as const } : s
          )
        );
      }, startDelay);
      timersRef.current.push(startTimer);

      const endTimer = setTimeout(() => {
        setStages((prev) =>
          prev.map((s, i) =>
            i === index ? { ...s, status: 'completed' as const } : s
          )
        );

        if (index === PIPELINE_STAGES.length - 1) {
          setTimeout(() => {
            setResult(getAffidavitResult());
            setAppState('complete');
          }, 300);
        }
      }, endDelay);
      timersRef.current.push(endTimer);
    });
  }, [canGenerate]);

  const handleDownload = useCallback(() => {
    downloadDocx();
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

          <div className="space-y-4">
            <ReferenceFormatStatus />

            <CaseInformationUpload
              file={caseFile}
              onFileSelected={(f) =>
                setCaseFile({ name: f.name, size: f.size })
              }
            />
          </div>

          <div className="flex justify-center mt-6">
            <Button
              size="lg"
              onClick={handleGenerate}
              disabled={!canGenerate}
              className="gap-2 min-w-[200px]"
            >
              <Sparkles className="h-4 w-4" />
              Generate Affidavit
            </Button>
          </div>

          {!canGenerate && appState === 'idle' && (
            <p className="text-center text-xs text-muted-foreground mt-3">
              Upload the Case Information PDF to enable generation
            </p>
          )}
        </section>

        {/* Processing Pipeline */}
        {appState !== 'idle' && (
          <section>
            <ProcessingPipeline stages={stages} />
          </section>
        )}

        {/* Results */}
        {appState === 'complete' && result && (
          <>
            <section>
              <CaseInformation data={result.caseInformation} />
            </section>

            <section>
              <AffidavitPreview
                text={result.affidavitText}
                onDownload={handleDownload}
              />
            </section>

            <section>
              <h2 className="text-xl font-semibold text-foreground mb-4">
                Evaluation Report
              </h2>
              <div className="space-y-4">
                <EvaluationSummary
                  report={result.evaluation}
                  validation={result.deterministicValidation}
                />
                <EvaluationCriteria criteria={result.evaluation.criteria} />
              </div>
            </section>

            <section>
              <DeterministicChecks result={result.deterministicValidation} />
            </section>

            <section>
              <IssuesSection issues={result.issues} />
            </section>
          </>
        )}

        {/* Workflow Explanation */}
        <WorkflowExplanation />

        {/* Footer */}
        <footer className="pt-8 pb-4 border-t border-border">
          <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
            <FileText className="h-3.5 w-3.5" />
            <span>Legal Affidavit Agent — Frontend Demo</span>
          </div>
        </footer>
      </main>
    </div>
  );
}

export default App;
