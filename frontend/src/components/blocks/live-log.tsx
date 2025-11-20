import { ScrollText } from "lucide-react";

interface LiveLogProps {
  title?: string;
  entries?: { id?: string | number; speaker?: string; message: string; timestamp?: string }[];
}

export function LiveLog({ title = "Board Meeting Live Log", entries = [] }: LiveLogProps) {
  return (
    <section className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-card)]/80 p-6 shadow-inner">
      <header className="mb-4 flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--color-primary)]/15 text-[var(--color-primary)]">
            <ScrollText className="h-5 w-5" />
          </span>
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-[var(--color-muted)]">Live Feed</p>
            <h3 className="text-lg font-semibold text-[var(--color-text)]">{title}</h3>
          </div>
        </div>
        <span className="inline-flex items-center gap-2 rounded-full bg-[var(--color-primary)]/15 px-3 py-1 text-xs font-medium text-[var(--color-primary)]">
          <span className="h-2 w-2 rounded-full bg-[var(--color-primary)]" />
          streaming
        </span>
      </header>
      <div className="space-y-3 overflow-hidden rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]/70 p-4 text-sm text-[var(--color-text)]">
        {entries.length === 0 ? (
          <p className="text-[var(--color-muted)]">Awaiting first dispatch from the Board...</p>
        ) : (
          entries.map((entry, idx) => (
            <div key={entry.id ?? idx} className="grid gap-1 rounded-lg border border-transparent p-3 transition hover:border-[var(--color-border)]">
              <div className="flex items-center justify-between text-xs text-[var(--color-muted)]">
                <span className="font-semibold text-[var(--color-text)]">{entry.speaker ?? "Agent"}</span>
                <span>{entry.timestamp ?? "now"}</span>
              </div>
              <p className="leading-relaxed text-[var(--color-text)]">{entry.message}</p>
            </div>
          ))
        )}
      </div>
    </section>
  );
}
