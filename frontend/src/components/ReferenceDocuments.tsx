import { CheckCircle2, FileText } from 'lucide-react';
import { PRELOADED_REFERENCE_DOCUMENTS } from '@/lib/api';

export function ReferenceDocuments() {
  return (
    <div>
      <h3 className="text-sm font-semibold text-foreground mb-3">
        Reference Documents
      </h3>
      <div className="space-y-3">
        {PRELOADED_REFERENCE_DOCUMENTS.map((doc) => (
          <div
            key={doc.file_name}
            className="flex items-center gap-3 rounded-lg border border-border bg-card px-4 py-3"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-muted shrink-0">
              <FileText className="h-4 w-4 text-muted-foreground" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-foreground truncate">
                {doc.file_name}
              </p>
              <p className="text-xs text-muted-foreground truncate">
                {doc.description}
              </p>
            </div>
            <div className="flex items-center gap-1.5 text-sm text-success shrink-0">
              <CheckCircle2 className="h-4 w-4" />
              <span className="font-medium">Loaded</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}