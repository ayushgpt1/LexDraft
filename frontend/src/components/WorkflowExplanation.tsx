import { Info } from 'lucide-react';

export function WorkflowExplanation() {
  return (
    <section className="rounded-lg border border-border bg-card p-6">
      <div className="flex items-center gap-2.5 mb-3">
        <Info className="h-4 w-4 text-muted-foreground" />
        <h2 className="text-base font-semibold text-foreground">
          How it works
        </h2>
      </div>
      <p className="text-sm text-muted-foreground leading-relaxed max-w-3xl">
        The system extracts structured case information, maps the reply points,
        generates an Affidavit in Reply using the preloaded reference format,
        validates the generated document using deterministic checks, and
        evaluates it using an LLM.
      </p>
    </section>
  );
}
