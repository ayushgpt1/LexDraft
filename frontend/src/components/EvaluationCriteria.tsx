import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import type { EvaluationCriterion } from '@/lib/types';

interface EvaluationCriteriaProps {
  criteria: EvaluationCriterion[];
}

export function EvaluationCriteria({ criteria }: EvaluationCriteriaProps) {
  return (
    <Card>
      <CardContent className="p-6">
        <h3 className="text-sm font-semibold text-foreground mb-4">
          LLM Evaluation Criteria
        </h3>
        <div className="space-y-4">
          {criteria.map((criterion) => (
            <div key={criterion.name}>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-sm text-foreground">{criterion.name}</span>
                <span className="text-sm font-medium text-muted-foreground">
                  {criterion.score} / {criterion.maxScore}
                </span>
              </div>
              <Progress
                value={(criterion.score / criterion.maxScore) * 100}
                className="h-2"
              />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
