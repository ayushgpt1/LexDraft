import { AlertCircle, Check, Loader2, Circle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import type { PipelineStage } from '@/lib/types';
import { cn } from '@/lib/utils';

interface ProcessingPipelineProps {
  stages: PipelineStage[];
}

export function ProcessingPipeline({ stages }: ProcessingPipelineProps) {
  return (
    <Card className="animate-fade-in-up">
      <CardContent className="p-6">
        <h2 className="text-base font-semibold text-foreground mb-6">
          Processing
        </h2>
        <div className="space-y-1">
          {stages.map((stage, index) => {
            const isLast = index === stages.length - 1;
            return (
              <div key={stage.id} className="flex gap-4">
                <div className="flex flex-col items-center">
                  <div
                    className={cn(
                      'flex h-9 w-9 items-center justify-center rounded-full border-2 transition-colors',
                      stage.status === 'completed' &&
                        'border-success bg-success text-success-foreground',
                      stage.status === 'processing' &&
                        'border-accent bg-accent text-accent-foreground',
                      stage.status === 'error' &&
                        'border-destructive bg-destructive text-destructive-foreground',
                      stage.status === 'pending' &&
                        'border-border bg-card text-muted-foreground'
                    )}
                  >
                    {stage.status === 'completed' && (
                      <Check className="h-4 w-4" />
                    )}
                    {stage.status === 'processing' && (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    )}
                    {stage.status === 'error' && (
                      <AlertCircle className="h-4 w-4" />
                    )}
                    {stage.status === 'pending' && (
                      <Circle className="h-3 w-3" />
                    )}
                  </div>
                  {!isLast && (
                    <div
                      className={cn(
                        'w-0.5 flex-1 min-h-[2rem] transition-colors',
                        stage.status === 'completed'
                          ? 'bg-success'
                          : 'bg-border'
                      )}
                    />
                  )}
                </div>
                <div className="pb-6 pt-1.5">
                  <p
                    className={cn(
                      'text-sm font-medium transition-colors',
                      stage.status === 'completed' && 'text-foreground',
                      stage.status === 'processing' && 'text-foreground',
                      stage.status === 'error' && 'text-foreground',
                      stage.status === 'pending' && 'text-muted-foreground'
                    )}
                  >
                    {stage.label}
                  </p>
                  {stage.status === 'processing' && (
                    <p className="text-xs text-muted-foreground mt-0.5 animate-pulse-soft">
                      Processing
                    </p>
                  )}
                  {stage.status === 'completed' && (
                    <p className="text-xs text-success mt-0.5">Complete</p>
                  )}
                  {stage.status === 'error' && (
                    <p className="text-xs text-destructive mt-0.5">Error</p>
                  )}
                  {stage.status === 'pending' && (
                    <p className="text-xs text-muted-foreground mt-0.5">
                      Waiting
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
