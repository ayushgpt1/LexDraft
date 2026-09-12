// ---------- Backend response types ----------
// These mirror backend/models/schemas.py, backend/core/orchestrator.py
// and backend/validation/validators.py exactly as returned by
// POST http://127.0.0.1:8000/generate (snake_case field names).

export interface Respondent {
  number: number;
  name: string;
}

export interface Deponent {
  name: string;
  designation: string | null;
  organisation: string | null;
  address: string | null;
  age: string | null;
  occupation: string | null;
}

export interface ReplyPoint {
  point_number: number;
  move_type: string;
  content: string[];
}

export interface CaseInformationData {
  document_type: string;
  court: string;
  jurisdiction: string;
  proceeding_type: string;
  case_number: string;
  year: number;
  petitioner: string;
  respondents: Respondent[];
  answering_respondent_number: number;
  deponent: Deponent;
  reply_points: ReplyPoint[];
  prayer: string[];
  verification_verb: string;
  place: string;
  date: string;
  advocate_firm: string | null;
  advocate_for: string | null;
}

export interface EvaluationCriterion {
  score: number;
  issues: string[];
}

export interface EvaluationReport {
  overall_score: number;
  entity_accuracy: EvaluationCriterion;
  completeness: EvaluationCriterion;
  semantic_faithfulness: EvaluationCriterion;
  hallucination: EvaluationCriterion;
  template_fidelity: EvaluationCriterion;
  overall_issues: string[];
}

export interface GeneratedParagraph {
  paragraph_number: number;
  content: string;
}

export interface GeneratedParagraphs {
  paragraphs: GeneratedParagraph[];
}

export interface ValidationResult {
  check: string;
  passed: boolean;
  issues: string[];
  expected?: unknown;
  found?: unknown;
  actual?: unknown;
}

export interface DeterministicScore {
  total_checks: number;
  passed_checks: number;
  failed_checks: number;
  score: number;
}

export interface GenerateResponse {
  message: string;
  download_url: string;
  deterministic_score: DeterministicScore;
  validation_results: ValidationResult[];
  evaluation_report: EvaluationReport;
  case_data: CaseInformationData;
  generated_paragraphs: GeneratedParagraphs;
}

// ---------- UI-only types ----------

export type StageStatus = 'pending' | 'processing' | 'completed' | 'error';

export interface PipelineStage {
  id: string;
  label: string;
  status: StageStatus;
}

// Progress events pushed by the backend over the /ws/progress socket.
export interface ProgressEvent {
  stage: string;
  status: 'processing' | 'complete' | 'error';
  message?: string;
}

export type UploadedFile = {
  name: string;
  size: number;
} | null;

export interface Issue {
  source: 'deterministic' | 'llm';
  message: string;
}
