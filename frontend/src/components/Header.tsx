import { Scale } from 'lucide-react';

export function Header() {
  return (
    <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="mx-auto max-w-5xl px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent text-accent-foreground">
            <Scale className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-lg font-semibold tracking-tight text-foreground">
              LexDraft
            </h1>
            <p className="text-sm text-muted-foreground">
              AI-powered Legal Affidavit Generation &amp; Evaluation Agent
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}
