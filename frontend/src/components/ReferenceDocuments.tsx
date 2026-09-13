import { useState, useCallback } from 'react';
import { CheckCircle2, FileText, Upload, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { PRELOADED_REFERENCE_DOCUMENTS, type PreloadedReferenceDocument } from '@/lib/api';

interface ReferenceDocumentsProps {
  /** Currently selected Format Explained file (user upload), if any. */
  formatFile: File | null;
  /** Currently selected Sample Affidavit file (user upload), if any. */
  sampleFile: File | null;
  /** Called when the user uploads a replacement Format Explained PDF. */
  onFormatChange: (file: File | null) => void;
  /** Called when the user uploads a replacement Sample Affidavit PDF. */
  onSampleChange: (file: File | null) => void;
}

function ReferenceFileCard({
  doc,
  currentFile,
  onReplace,
  onRevert,
}: {
  doc: PreloadedReferenceDocument;
  currentFile: File | null;
  onReplace: (file: File) => void;
  onRevert: () => void;
}) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (!file) return;

      if (file.type !== 'application/pdf') {
        setError('Please select a PDF file.');
        return;
      }

      setIsUploading(true);
      setError(null);

      // Simulate a brief processing delay for UX; the actual upload
      // happens later when Generate is clicked.
      setTimeout(() => {
        onReplace(file);
        setIsUploading(false);
        // Reset the input so the same file can be re-selected if needed.
        event.target.value = '';
      }, 150);
    },
    [onReplace]
  );

  const displayName = currentFile ? currentFile.name : doc.file_name;
  const isCustom = currentFile !== null;

  return (
    <div>
      <div
        className="flex items-center gap-3 rounded-lg border border-border bg-card px-4 py-3"
        style={{ transition: 'border-color 0.15s' }}
      >
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-muted shrink-0">
          <FileText className="h-4 w-4 text-muted-foreground" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-foreground truncate">
            {displayName}
          </p>
          <p className="text-xs text-muted-foreground truncate">
            {isCustom
              ? 'Custom reference document'
              : doc.description}
          </p>
        </div>
        <div className="flex items-center gap-1.5 text-sm text-success shrink-0">
          <CheckCircle2 className="h-4 w-4" />
          <span className="font-medium">{isCustom ? 'Replaced' : 'Loaded'}</span>
        </div>
      </div>

      <div className="mt-2 flex items-center gap-2">
        {isCustom ? (
          <>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => {
                onRevert();
                setError(null);
              }}
            >
              Use Default
            </Button>
          </>
        ) : (
          <>
            <label className="cursor-pointer text-xs text-muted-foreground underline underline-offset-2 hover:text-foreground">
              Replace Format
            </label>
            <input
              type="file"
              accept="application/pdf"
              onChange={handleFileChange}
              className="hidden"
              id={`replace-${doc.file_name.replace(/\s+/g, '-')}`}
            />
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() =>
                document.getElementById(`replace-${doc.file_name.replace(/\s+/g, '-')}`)?.click()
              }
              disabled={isUploading}
              className="gap-1"
            >
              {isUploading ? (
                <>
                  <Upload className="h-3 w-3 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="h-3 w-3" />
                  Replace
                </>
              )}
            </Button>
          </>
        )}
        {error && (
          <span className="text-xs text-destructive truncate">{error}</span>
        )}
      </div>
    </div>
  );
}

export function ReferenceDocuments({
  formatFile,
  sampleFile,
  onFormatChange,
  onSampleChange,
}: ReferenceDocumentsProps) {
  const formatDoc = PRELOADED_REFERENCE_DOCUMENTS.find(
    (d) => d.file_name === '01 Affidavit Format Explained.pdf'
  );
  const sampleDoc = PRELOADED_REFERENCE_DOCUMENTS.find(
    (d) => d.file_name === '02 Affidavit in Reply Sample.docx.pdf'
  );

  return (
    <div>
      <h3 className="text-sm font-semibold text-foreground mb-3">
        Reference Materials
      </h3>
      <div className="space-y-4">
        {formatDoc && (
          <ReferenceFileCard
            doc={formatDoc}
            currentFile={formatFile}
            onReplace={onFormatChange}
            onRevert={() => onFormatChange(null)}
          />
        )}
        {sampleDoc && (
          <ReferenceFileCard
            doc={sampleDoc}
            currentFile={sampleFile}
            onReplace={onSampleChange}
            onRevert={() => onSampleChange(null)}
          />
        )}
      </div>
    </div>
  );
}