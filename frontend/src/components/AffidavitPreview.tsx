import { Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { CaseInformationData, GeneratedParagraph } from '@/lib/types';

interface AffidavitPreviewProps {
  caseData: CaseInformationData;
  paragraphs: GeneratedParagraph[];
  onDownload: () => void;
}

/**
 * Replicates backend/core/document_generator.py: format_legal_date
 * Converts "5 September 2026" -> "5th day of September 2026"
 */
function formatLegalDate(dateString: string): string {
  if (!dateString) return dateString;
  const parts = dateString.split(' ');
  if (parts.length >= 3) {
    const day = parseInt(parts[0], 10);
    if (!isNaN(day)) {
      let suffix: string;
      if (day % 100 >= 10 && day % 100 <= 20) {
        suffix = 'th';
      } else {
        suffix = { 1: 'st', 2: 'nd', 3: 'rd' }[day % 10] || 'th';
      }
      parts[0] = `${day}${suffix}`;
    }
  }
  let formatted = parts.join(' ');
  if (!formatted.includes(' day of ')) {
    const formattedParts = formatted.split(' ');
    if (formattedParts.length >= 3) {
      formatted = `${formattedParts[0]} day of ${formattedParts[1]} ${formattedParts[2]}`;
    }
  }
  return formatted;
}

/**
 * Replicates backend/core/document_generator.py: get_jurat_affirmation
 */
function getJuratAffirmation(verificationVerb: string): string {
  const verb = verificationVerb.trim().toLowerCase();
  if (verb.includes('swear')) {
    return 'Sworn';
  }
  return 'Solemnly affirmed';
}

/**
 * Replicates backend/core/document_generator.py: case_data.proceeding_type.title()
 */
function toTitleCase(str: string): string {
  if (!str) return str;
  return str.replace(/\w\S*/g, (word) =>
    word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
  );
}

/**
 * Replicates the deponent-clause construction in
 * backend/core/document_generator.py (Section 4).
 */
function buildDeponentClause(data: CaseInformationData): string {
  const deponent = data.deponent;
  const isOrgDeponent = !!(deponent.organisation && deponent.designation);
  const capacityPhrase = isOrgDeponent
    ? `the ${deponent.designation} of the Respondent No.${data.answering_respondent_number} above named`
    : `the Respondent No.${data.answering_respondent_number} above named`;

  const parts = [`I, ${deponent.name}`];

  if (deponent.designation && !isOrgDeponent) {
    parts.push(deponent.designation);
  }

  if (deponent.address) {
    parts.push(`residing at ${deponent.address}`);
  }

  parts.push(capacityPhrase);

  return parts.join(', ') + `, do hereby ${data.verification_verb} and state as under:`;
}

export function AffidavitPreview({
  caseData,
  paragraphs,
  onDownload,
}: AffidavitPreviewProps) {
  const formattedDate = formatLegalDate(caseData.date);
  const juratVerb = getJuratAffirmation(caseData.verification_verb);
  const deponentClause = buildDeponentClause(caseData);
  const paragraphCount = paragraphs.length;
  const proceedingTypeTitle = toTitleCase(caseData.proceeding_type);

  // These three items are generated programmatically (never LLM-produced)
  // in backend/core/document_generator.py — Section 7.
  const prayerItems = [
    `dismiss the present ${proceedingTypeTitle} with costs;`,
    'refuse any interim or ad-interim relief sought by the Petitioner; and',
    "grant such other and further reliefs as this Hon'ble Court may deem fit and proper in the facts and circumstances of the case.",
  ];

  return (
    <div className="animate-fade-in-up">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-semibold text-foreground">
          Generated Affidavit
        </h2>
        <Button size="lg" onClick={onDownload} className="gap-2">
          <Download className="h-4 w-4" />
          Download DOCX
        </Button>
      </div>

      <div className="flex justify-center bg-gray-50 py-8">
        <div
          className="bg-white shadow-lg border border-border w-full max-w-[680px] px-12 sm:px-16 py-14 font-serif-legal text-black"
          style={{ minHeight: '400px' }}
        >
          {/* 1. COURT HEADING */}
          <div className="text-center mb-6">
            <p className="font-bold text-sm">{caseData.court.toUpperCase()}</p>
            <p className="font-bold text-sm mt-1">
              {caseData.jurisdiction.toUpperCase()}
            </p>
            <p className="font-bold text-sm mt-4">
              {caseData.proceeding_type.toUpperCase()} NO. {caseData.case_number}{' '}
              OF {caseData.year}
            </p>
          </div>

          {/* 2. CAUSE TITLE */}
          <div className="mb-6">
            <div className="flex justify-between">
              <span className="text-sm">{caseData.petitioner}</span>
              <span className="text-sm">...Petitioner</span>
            </div>
            <p className="text-center font-bold text-sm my-3">VERSUS</p>
            {caseData.respondents.map((respondent) => (
              <div className="flex justify-between" key={respondent.number}>
                <span className="text-sm">
                  {respondent.number}. {respondent.name}
                </span>
                <span className="text-sm">
                  ...Respondent No.{respondent.number}
                </span>
              </div>
            ))}
          </div>

          {/* 3. AFFIDAVIT TITLE */}
          <p className="text-center font-bold text-sm my-3">
            AFFIDAVIT IN REPLY ON BEHALF OF RESPONDENT NO.{' '}
            {caseData.answering_respondent_number}
          </p>

          {/* 4. DEPONENT CLAUSE */}
          <p className="text-justify text-sm ml-3 my-2 leading-tight">
            {deponentClause}
          </p>

          {/* 5. NUMBERED REPLY PARAGRAPHS */}
          {paragraphs.length === 0 ? (
            <p className="text-sm text-center my-6">
              No paragraphs were generated.
            </p>
          ) : (
            <div className="ml-3 space-y-4">
              {paragraphs.map((paragraph) => (
                <p
                  key={paragraph.paragraph_number}
                  className="text-justify text-sm leading-relaxed"
                >
                  <span className="font-semibold">
                    {paragraph.paragraph_number}.{' '}
                  </span>
                  {paragraph.content}
                </p>
              ))}
            </div>
          )}

          {/* 6. PAGE BREAK (matches doc.add_page_break() in backend) */}
          <div className="my-10 h-px bg-gray-300"></div>

          {/* 7. PRAYER */}
          <div className="mb-6">
            <p className="text-center font-bold text-sm mb-3">PRAYER</p>
            <p className="text-justify text-sm mb-3">
              I therefore respectfully pray that this Hon'ble Court may be
              pleased to:
            </p>
            <div className="ml-4">
              {prayerItems.map((item, index) => {
                const letter = String.fromCharCode(96 + index + 1);
                return (
                  <p
                    key={index}
                    className="text-justify text-sm mb-1"
                    style={{
                      marginLeft: '1.5rem',
                      textIndent: '-1.5rem',
                    }}
                  >
                    <span className="font-bold">({letter}) </span>
                    {item}
                  </p>
                );
              })}
            </div>
          </div>

          {/* 8. JURAT */}
          <div className="mb-6">
            <p className="text-sm mb-0.5">
              {juratVerb} at {caseData.place}
            </p>
            <p className="text-sm mb-2.5">On this {formattedDate}</p>
            <div className="flex justify-between">
              <span className="text-sm">Before Me</span>
              <strong className="text-sm">DEPONENT</strong>
            </div>
          </div>

          {/* 9. VERIFICATION */}
          <div className="mb-6">
            <p className="text-center font-bold text-sm mb-3">VERIFICATION</p>
            <p className="text-justify text-sm mb-2">
              I, {caseData.deponent.name}, the Deponent above named, do hereby
              verify that the contents of paragraphs 1 to {paragraphCount} and the
              Prayer above are true and correct to my knowledge and belief and
              that nothing material has been concealed therefrom.
            </p>
            <p className="text-justify text-sm mb-3">
              Verified at {caseData.place} on this {formattedDate}.
            </p>
            <p className="text-right font-bold text-sm">DEPONENT</p>
          </div>

          {/* 10. ADVOCATE BLOCK (only when advocate_firm is provided) */}
          {caseData.advocate_firm && (
            <div className="ml-3">
              <p className="text-justify text-sm font-bold mb-1">
                {caseData.advocate_firm}
              </p>
              {caseData.advocate_for && (
                <p className="text-justify text-sm">
                  Advocate for {caseData.advocate_for}
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}