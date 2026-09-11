import { CheckCircle2, FileText } from 'lucide-react';

export function ReferenceFormatStatus() {
  return (
    <div className="flex items-center gap-3 rounded-lg border border-border bg-card px-4 py-3">
      <div className="flex h-8 w-8 items-center justify-center rounded-md bg-muted">
        <FileText className="h-4 w-4 text-muted-foreground" />
      </div>
      <div className="flex-1">
        <p className="text-sm font-medium text-foreground">Reference Format</p>
        <p className="text-xs text-muted-foreground">
          Affidavit in Reply format
        </p>
      </div>
      <div className="flex items-center gap-1.5 text-sm text-success">
        <CheckCircle2 className="h-4 w-4" />
        <span className="font-medium">Loaded</span>
      </div>
    </div>
  );
}
