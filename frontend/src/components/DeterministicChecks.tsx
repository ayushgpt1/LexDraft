import { CheckCircle2, XCircle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { DeterministicScore, ValidationResult } from '@/lib/types';

interface DeterministicChecksProps {
  checks: ValidationResult[];
  score: DeterministicScore;
}

export function DeterministicChecks({ checks, score }: DeterministicChecksProps) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-foreground">
            Deterministic Checks
          </h3>
          <Badge
            variant="secondary"
            className="text-xs"
          >
            {score.passed_checks} / {score.total_checks} checks passed
          </Badge>
        </div>

        <div className="mb-4">
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold text-foreground">
              {Math.round(score.score)}%
            </span>
            {score.failed_checks === 0 ? (
              <span className="text-xs text-success font-medium">
                All checks passed
              </span>
            ) : (
              <span className="text-xs text-destructive font-medium">
                {score.failed_checks} {score.failed_checks === 1 ? 'check' : 'checks'} failed
              </span>
            )}
          </div>
        </div>

        <div className="space-y-3">
          {checks.map((check) => (
            <div key={check.check}>
              <div className="flex items-center gap-2.5 text-sm">
                {check.passed ? (
                  <CheckCircle2 className="h-4 w-4 text-success shrink-0" />
                ) : (
                  <XCircle className="h-4 w-4 text-destructive shrink-0" />
                )}
                <span className={check.passed ? 'text-foreground' : 'text-destructive'}>
                  {check.check}
                </span>
              </div>
              {!check.passed && check.issues.length > 0 && (
                <ul className="mt-1 ml-7 space-y-0.5">
                  {check.issues.map((issue, i) => (
                    <li key={i} className="text-xs text-destructive">
                      {issue}
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
