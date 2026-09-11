import { CheckCircle2, XCircle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { DeterministicValidationResult } from '@/lib/types';

interface DeterministicChecksProps {
  result: DeterministicValidationResult;
}

export function DeterministicChecks({ result }: DeterministicChecksProps) {
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
            {result.passedCount} / {result.totalCount} checks passed
          </Badge>
        </div>

        <div className="mb-4">
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold text-foreground">
              {result.score}%
            </span>
            <span className="text-xs text-success font-medium">
              All checks passed
            </span>
          </div>
        </div>

        <div className="space-y-2.5">
          {result.checks.map((check) => (
            <div
              key={check.name}
              className="flex items-center gap-2.5 text-sm"
            >
              {check.passed ? (
                <CheckCircle2 className="h-4 w-4 text-success shrink-0" />
              ) : (
                <XCircle className="h-4 w-4 text-destructive shrink-0" />
              )}
              <span className={check.passed ? 'text-foreground' : 'text-destructive'}>
                {check.name}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
