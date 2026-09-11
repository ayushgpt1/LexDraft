export type StageStatus = 'pending' | 'processing' | 'completed';

export type UploadedFile = {
  name: string;
  size: number;
} | null;

export interface PipelineStage {
  id: string;
  label: string;
  status: StageStatus;
}

export interface CaseInformationData {
  documentType: string;
  court: string;
  jurisdiction: string;
  proceedingType: string;
  caseNumber: string;
  year: string;
  petitioner: string;
  respondents: string[];
  answeringRespondent: string;
  deponent: string;
  designation: string;
  organisation: string;
  address: string;
  place: string;
  date: string;
  replyPoints: string[];
}

export interface EvaluationCriterion {
  name: string;
  score: number;
  maxScore: number;
}

export interface DeterministicCheck {
  name: string;
  passed: boolean;
}

export interface EvaluationReport {
  deterministicScore: number;
  llmScore: number;
  llmMaxScore: number;
  criteria: EvaluationCriterion[];
}

export interface DeterministicValidationResult {
  checks: DeterministicCheck[];
  passedCount: number;
  totalCount: number;
  score: number;
}

export interface Issue {
  source: 'deterministic' | 'llm';
  message: string;
}

export interface AffidavitResult {
  caseInformation: CaseInformationData;
  affidavitText: string;
  evaluation: EvaluationReport;
  deterministicValidation: DeterministicValidationResult;
  issues: Issue[];
}
