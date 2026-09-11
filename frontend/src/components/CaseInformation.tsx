import { useState } from 'react';
import { ChevronDown, Info } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import type { CaseInformationData } from '@/lib/types';

interface CaseInformationProps {
  data: CaseInformationData;
}

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <dt className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
        {label}
      </dt>
      <dd className="mt-0.5 text-sm text-foreground">{value}</dd>
    </div>
  );
}

export function CaseInformation({ data }: CaseInformationProps) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <Card className="animate-fade-in-up">
      <CardContent className="p-0">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex w-full items-center justify-between p-6"
        >
          <div className="flex items-center gap-2.5">
            <Info className="h-4 w-4 text-muted-foreground" />
            <h2 className="text-base font-semibold text-foreground">
              Case Information
            </h2>
          </div>
          <ChevronDown
            className={cn(
              'h-5 w-5 text-muted-foreground transition-transform',
              isOpen && 'rotate-180'
            )}
          />
        </button>

        {isOpen && (
          <div className="px-6 pb-6">
            <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-4">
              <Field label="Document Type" value={data.documentType} />
              <Field label="Court" value={data.court} />
              <Field label="Jurisdiction" value={data.jurisdiction} />
              <Field label="Proceeding Type" value={data.proceedingType} />
              <Field label="Case Number" value={data.caseNumber} />
              <Field label="Year" value={data.year} />
              <Field label="Petitioner" value={data.petitioner} />
              <Field
                label="Respondents"
                value={
                  <ol className="list-decimal list-inside space-y-0.5">
                    {data.respondents.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ol>
                }
              />
              <Field label="Answering Respondent" value={data.answeringRespondent} />
              <Field label="Deponent" value={data.deponent} />
              <Field label="Designation" value={data.designation} />
              <Field label="Organisation" value={data.organisation} />
              <Field label="Address" value={data.address} />
              <Field label="Place" value={data.place} />
              <Field label="Date" value={data.date} />
            </dl>

            <div className="mt-6 pt-4 border-t border-border">
              <dt className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-3">
                Reply Points
              </dt>
              <div className="flex flex-wrap gap-2">
                {data.replyPoints.map((point, i) => (
                  <Badge
                    key={i}
                    variant="secondary"
                    className="text-xs font-normal"
                  >
                    {i + 1}. {point}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
