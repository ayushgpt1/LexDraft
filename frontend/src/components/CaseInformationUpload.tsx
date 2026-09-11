import { useRef, useState } from 'react';
import { FileText, Upload, CheckCircle2 } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import type { UploadedFile } from '@/lib/types';

interface CaseInformationUploadProps {
  file: UploadedFile;
  onFileSelected: (file: File) => void;
}

export function CaseInformationUpload({
  file,
  onFileSelected,
}: CaseInformationUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFile = (f: File) => {
    if (f && f.type === 'application/pdf') {
      onFileSelected(f);
    }
  };

  return (
    <Card
      className={`transition-colors ${
        isDragging ? 'border-accent border-2' : ''
      }`}
    >
      <CardContent className="p-6">
        <div className="mb-4">
          <h3 className="text-base font-semibold text-foreground">
            Case Information
          </h3>
          <p className="text-sm text-muted-foreground mt-0.5">
            Upload the case information document
          </p>
        </div>

        <div
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setIsDragging(false);
            if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
          }}
          className={`flex flex-col items-center justify-center rounded-lg border-2 border-dashed py-8 px-4 transition-colors ${
            file
              ? 'border-success/40 bg-success/5'
              : isDragging
                ? 'border-accent bg-accent/5'
                : 'border-border bg-muted/30'
          }`}
        >
          {file ? (
            <div className="flex flex-col items-center gap-3 text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-success/10">
                <FileText className="h-6 w-6 text-success" />
              </div>
              <div>
                <p className="text-sm font-medium text-foreground">{file.name}</p>
                <div className="mt-1 flex items-center gap-1.5 text-xs text-success">
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  <span>Ready</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-3 text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-muted">
                <Upload className="h-6 w-6 text-muted-foreground" />
              </div>
              <p className="text-xs text-muted-foreground">
                Drag & drop PDF or click to browse
              </p>
            </div>
          )}
        </div>

        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={(e) => {
            if (e.target.files?.[0]) handleFile(e.target.files[0]);
          }}
        />

        <Button
          variant={file ? 'outline' : 'default'}
          className="mt-4 w-full"
          onClick={() => inputRef.current?.click()}
        >
          {file ? 'Replace PDF' : 'Upload Case Information PDF'}
        </Button>
      </CardContent>
    </Card>
  );
}
