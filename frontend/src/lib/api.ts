import type { AffidavitResult } from './types';
import {
  mockCaseInformation,
  mockAffidavitText,
  mockEvaluation,
  mockDeterministicValidation,
  mockIssues,
} from './mockData';

export const PIPELINE_STAGES = [
  'Extract Case Information',
  'Map Reply Points',
  'Generate Affidavit',
  'Validate Document',
  'Evaluate Document',
] as const;

export const STAGE_DURATION_MS = 1200;

export function getAffidavitResult(): AffidavitResult {
  return {
    caseInformation: mockCaseInformation,
    affidavitText: mockAffidavitText,
    evaluation: mockEvaluation,
    deterministicValidation: mockDeterministicValidation,
    issues: mockIssues,
  };
}

export function downloadDocx(): void {
  const blob = new Blob([mockAffidavitText], {
    type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'Affidavit_in_Reply.docx';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
