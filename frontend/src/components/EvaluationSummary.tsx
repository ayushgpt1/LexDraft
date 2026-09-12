import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { ShieldCheck, Brain } from 'lucide-react';
import type { DeterministicScore, EvaluationReport } from '@/lib/types';

interface EvaluationSummaryProps {
  report: EvaluationReport;
  deterministic: DeterministicScore;
}

export function EvaluationSummary({ report, deterministic }: EvaluationSummaryProps) {
  return (
    <div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-2 mb-3">
              <ShieldCheck className="h-4 w-4 text-success" />
              <h3 className="text-sm font-medium text-muted-foreground">
                Deterministic Score
              </h3>
            </div>
            <p className="text-3xl font-bold text-foreground">
              {Math.round(deterministic.score)}
              <span className="text-lg text-muted-foreground">%</span>
            </p>
            <p className="text-xs text-muted-foreground mt-1.5">
              {deterministic.passed_checks} / {deterministic.total_checks} checks passed
            </p>
            <Progress
              value={deterministic.score}
              className="mt-3 h-1.5"
            />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-2 mb-3">
              <Brain className="h-4 w-4 text-accent" />
              <h3 className="text-sm font-medium text-muted-foreground">
                LLM Evaluation
              </h3>
            </div>
            <p className="text-3xl font-bold text-foreground">
              {report.overall_score}
              <span className="text-lg text-muted-foreground">%</span>
            </p>
            <p className="text-xs text-muted-foreground mt-1.5">
              Overall score across all evaluation criteria
            </p>
            <Progress
              value={report.overall_score}
              className="mt-3 h-1.5"
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
