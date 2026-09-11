import { AlertCircle, CheckCircle2 } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { Issue } from '@/lib/types';

interface IssuesSectionProps {
  issues: Issue[];
}

export function IssuesSection({ issues }: IssuesSectionProps) {
  const hasIssues = issues.length > 0;

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-foreground">Issues</h3>
          <Badge variant={hasIssues ? 'destructive' : 'secondary'} className="text-xs">
            {issues.length} {issues.length === 1 ? 'issue' : 'issues'}
          </Badge>
        </div>

        {hasIssues ? (
          <div className="space-y-2">
            {issues.map((issue, i) => (
              <div
                key={i}
                className="flex items-start gap-2.5 rounded-md border border-destructive/30 bg-destructive/5 p-3"
              >
                <AlertCircle className="h-4 w-4 text-destructive shrink-0 mt-0.5" />
                <div>
                  <span className="text-xs font-medium text-destructive uppercase tracking-wide">
                    {issue.source}
                  </span>
                  <p className="text-sm text-foreground mt-0.5">
                    {issue.message}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex items-center gap-2.5 text-sm text-muted-foreground">
            <CheckCircle2 className="h-4 w-4 text-success" />
            <span>No issues detected.</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
