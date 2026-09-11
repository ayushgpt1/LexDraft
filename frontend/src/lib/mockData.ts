import type {
  CaseInformationData,
  EvaluationReport,
  DeterministicValidationResult,
  Issue,
} from './types';

export const pipelineStageLabels = [
  'Extract Case Information',
  'Map Reply Points',
  'Generate Affidavit',
  'Validate Document',
  'Evaluate Document',
] as const;

export const mockCaseInformation: CaseInformationData = {
  documentType: 'Affidavit in Reply',
  court: 'IN THE HIGH COURT OF JUDICATURE AT BOMBAY',
  jurisdiction: 'ORDINARY ORIGINAL CIVIL JURISDICTION',
  proceedingType: 'WRIT PETITION',
  caseNumber: '1847',
  year: '2026',
  petitioner: 'Sunrise Housing Private Limited',
  respondents: [
    'State of Maharashtra',
    'Mumbai Metropolitan Region Development Authority',
  ],
  answeringRespondent: 'Respondent No. 2',
  deponent: 'Arvind Rajan',
  designation: 'Deputy Metropolitan Commissioner',
  organisation: 'Mumbai Metropolitan Region Development Authority',
  address: 'Bandra East, Mumbai, Maharashtra',
  place: 'Mumbai',
  date: '5 September 2026',
  replyPoints: [
    'Filing of Affidavit in Reply',
    'General Denial',
    'Preliminary Position',
    'Denial Regarding Communication',
    'Authority for Communication',
    'Document Relied Upon',
  ],
};

export const mockAffidavitText = `IN THE HIGH COURT OF JUDICATURE AT BOMBAY

ORDINARY ORIGINAL CIVIL JURISDICTION

WRIT PETITION NO. 1847 OF 2026

Sunrise Housing Private Limited ...Petitioner

VERSUS

1. State of Maharashtra ...Respondent No.1
2. Mumbai Metropolitan Region Development Authority ...Respondent No.2

AFFIDAVIT IN REPLY ON BEHALF OF RESPONDENT NO. 2

I, Arvind Rajan, Deputy Metropolitan Commissioner, residing at Bandra East, Mumbai, Maharashtra, the Respondent No.2 above named, do hereby solemnly affirm and state as under:

1. The deponent has perused a copy of the Writ Petition filed by Sunrise Housing Private Limited. The deponent is filing this Affidavit in Reply on behalf of Respondent No. 2, Mumbai Metropolitan Region Development Authority, to oppose the contentions raised in the Writ Petition and the reliefs sought by the Petitioner.

2. Respondent No. 2 denies all statements, contentions and averments made in the Writ Petition except those specifically admitted in this Affidavit in Reply. Nothing contained in the Writ Petition that has not been specifically dealt with or admitted is to be treated as an admission by Respondent No. 2.

3. The Writ Petition is misconceived and devoid of merits. The actions challenged by the Petitioner were taken in accordance with the applicable redevelopment procedure and within the authority available to Respondent No. 2.

4. Respondent No. 2 denies that the impugned communication dated 15 July 2026 was issued without authority.

5. The communication dated 15 July 2026 was issued pursuant to the applicable redevelopment procedure and after consideration of the relevant records.

6. Respondent No. 2 relies upon the communication dated 15 July 2026. A copy of that communication is to be annexed and marked as EXHIBIT-'A'.

7. In view of the foregoing, the Writ Petition is liable to be dismissed with costs.

PRAYER

I therefore respectfully pray that this Hon'ble Court may be pleased to:

(a) dismiss the present Writ Petition with costs;

(b) refuse any interim or ad-interim relief sought by the Petitioner; and

(c) grant such other and further reliefs as this Hon'ble Court may deem fit and proper in the facts and circumstances of the case.

Solemnly affirmed at Mumbai

On this 5th day of September 2026

Before Me                                      DEPONENT

VERIFICATION

I, Arvind Rajan, the Deponent above named, do hereby verify that the contents of paragraphs 1 to 7 and the Prayer above are true and correct to my knowledge and belief and that nothing material has been concealed therefrom.

Verified at Mumbai on this 5th day of September 2026.

DEPONENT

Rajan & Associates

Advocate for Respondent No. 2`;

export const mockEvaluation: EvaluationReport = {
  deterministicScore: 100,
  llmScore: 96,
  llmMaxScore: 100,
  criteria: [
    { name: 'Entity Accuracy', score: 100, maxScore: 100 },
    { name: 'Completeness', score: 95, maxScore: 100 },
    { name: 'Semantic Faithfulness', score: 95, maxScore: 100 },
    { name: 'Hallucination', score: 95, maxScore: 100 },
    { name: 'Template Fidelity', score: 95, maxScore: 100 },
  ],
};

export const mockDeterministicValidation: DeterministicValidationResult = {
  checks: [
    { name: 'Respondent consistency', passed: true },
    { name: 'Case number consistency', passed: true },
    { name: 'Date consistency', passed: true },
    { name: 'Exhibit consistency', passed: true },
    { name: 'Required sections and order', passed: true },
    { name: 'Paragraph numbering', passed: true },
    { name: 'Verification range', passed: true },
  ],
  passedCount: 7,
  totalCount: 7,
  score: 100,
};

export const mockIssues: Issue[] = [];
