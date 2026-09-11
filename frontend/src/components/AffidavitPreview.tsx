import { Download } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface AffidavitPreviewProps {
  text: string;
  onDownload: () => void;
}

export function AffidavitPreview({ text, onDownload }: AffidavitPreviewProps) {
  const lines = text.split('\n');

  return (
    <div className="animate-fade-in-up">
      <h2 className="text-base font-semibold text-foreground mb-4">
        Generated Affidavit
      </h2>

      <div className="flex justify-center">
        <div
          className="bg-white shadow-lg border border-border w-full max-w-[680px] px-12 sm:px-16 py-14 font-serif-legal text-black"
          style={{ minHeight: '400px' }}
        >
          <div className="space-y-0">
            {lines.map((line, i) => {
              const trimmed = line.trim();
              if (trimmed === '') {
                return <div key={i} className="h-4" />;
              }

              const isCourtHeader = trimmed.startsWith('IN THE HIGH COURT');
              const isJurisdiction = trimmed === 'ORDINARY ORIGINAL CIVIL JURISDICTION';
              const isPetitionLine = trimmed.startsWith('WRIT PETITION NO.');
              const isVersus = trimmed === 'VERSUS';
              const isAffidavitTitle = trimmed.startsWith('AFFIDAVIT IN REPLY');
              const isPrayer = trimmed === 'PRAYER';
              const isVerification = trimmed === 'VERIFICATION';
              const isPartyLine =
                trimmed.includes('...Petitioner') ||
                trimmed.includes('...Respondent');
              const isAdvocate = trimmed.startsWith('Rajan & Associates') ||
                trimmed.startsWith('Advocate for');
              const isBeforeMe = trimmed.includes('Before Me');
              const isNumbered = /^\d+\.\s/.test(trimmed);
              const isPrayerItem = /^\([a-c]\)/.test(trimmed);

              if (
                isCourtHeader ||
                isJurisdiction ||
                isPetitionLine ||
                isAffidavitTitle
              ) {
                return (
                  <p key={i} className="text-center font-bold uppercase tracking-wide text-sm leading-relaxed">
                    {trimmed}
                  </p>
                );
              }

              if (isVersus) {
                return (
                  <p key={i} className="text-center font-bold italic my-2 text-sm">
                    {trimmed}
                  </p>
                );
              }

              if (isPrayer || isVerification) {
                return (
                  <p key={i} className="text-center font-bold uppercase tracking-wide text-sm mt-6 mb-2">
                    {trimmed}
                  </p>
                );
              }

              if (isPartyLine) {
                return (
                  <p key={i} className="text-sm leading-relaxed">
                    {trimmed}
                  </p>
                );
              }

              if (isBeforeMe) {
                return (
                  <p key={i} className="flex justify-between text-sm leading-relaxed mt-8">
                    <span>{trimmed.split('DEPONENT')[0].trim()}</span>
                    <span className="font-bold">DEPONENT</span>
                  </p>
                );
              }

              if (isNumbered || isPrayerItem) {
                return (
                  <p key={i} className="text-justify text-sm leading-relaxed indent-6">
                    {trimmed}
                  </p>
                );
              }

              if (isAdvocate) {
                return (
                  <p
                    key={i}
                    className={`text-sm leading-relaxed ${i === lines.length - 1 ? 'font-bold' : ''}`}
                  >
                    {trimmed}
                  </p>
                );
              }

              return (
                <p key={i} className="text-justify text-sm leading-relaxed">
                  {trimmed}
                </p>
              );
            })}
          </div>
        </div>
      </div>

      <div className="flex justify-center mt-6">
        <Button size="lg" onClick={onDownload} className="gap-2">
          <Download className="h-4 w-4" />
          Download DOCX
        </Button>
      </div>
    </div>
  );
}
