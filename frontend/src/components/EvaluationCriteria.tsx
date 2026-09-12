import { AlertCircle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import type { EvaluationCriterion } from '@/lib/types';

export interface NamedCriterion {
  name: string;
  criterion: EvaluationCriterion;
}

interface EvaluationCriteriaProps {
  criteria: NamedCriterion[];
}

export function EvaluationCriteria({ criteria }: EvaluationCriteriaProps) {
  return (
    <Card>
      <CardContent className="p-6">
        <h3 className="text-sm font-semibold text-foreground mb-4">
          LLM Evaluation Criteria
        </h3>
        <div className="space-y-5">
          {criteria.map(({ name, criterion }) => (
            <div key={name}>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-sm text-foreground">{name}</span>
                <span className="text-sm font-medium text-muted-foreground">
                  {criterion.score} / 100
                </span>
              </div>
              <Progress
                value={criterion.score}
                className="h-2"
              />
              {criterion.issues.length > 0 && (
                <ul className="mt-2 space-y-1">
                  {criterion.issues.map((issue, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-1.5 text-xs text-destructive"
                    >
                      <AlertCircle className="h-3.5 w-3.5 shrink-0 mt-0.5" />
                      <span>{issue}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
