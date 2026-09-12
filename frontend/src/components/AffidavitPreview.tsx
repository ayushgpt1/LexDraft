import { Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { GeneratedParagraph } from '@/lib/types';

interface AffidavitPreviewProps {
  paragraphs: GeneratedParagraph[];
  onDownload: () => void;
}

export function AffidavitPreview({ paragraphs, onDownload }: AffidavitPreviewProps) {
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
          {paragraphs.length === 0 ? (
            <p className="text-sm text-center">No paragraphs were generated.</p>
          ) : (
            <div className="space-y-4">
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
