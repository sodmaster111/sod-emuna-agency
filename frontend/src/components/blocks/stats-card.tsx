import type { ElementType } from "react";

interface StatsCardProps {
  label: string;
  value: string | number;
  description?: string;
  icon?: ElementType;
  trend?: { direction: "up" | "down"; value: string };
}

export function StatsCard({ label, value, description, icon: Icon, trend }: StatsCardProps) {
  return (
    <div className="group relative overflow-hidden rounded-2xl border border-[var(--color-border)] bg-[var(--color-card)] p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-[var(--color-primary)]/60">
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.2em] text-[var(--color-muted)]">{label}</p>
          <div className="flex items-center gap-2 text-3xl font-semibold text-[var(--color-text)]">
            <span>{value}</span>
            {trend ? (
              <span
                className={`text-xs font-semibold ${
                  trend.direction === "up" ? "text-green-400" : "text-red-400"
                }`}
              >
                {trend.direction === "up" ? "▲" : "▼"} {trend.value}
              </span>
            ) : null}
          </div>
          {description ? <p className="text-sm text-[var(--color-muted)]">{description}</p> : null}
        </div>
        {Icon ? (
          <span className="rounded-xl bg-[var(--color-primary)]/15 p-3 text-[var(--color-primary)]">
            <Icon className="h-5 w-5" />
          </span>
        ) : null}
      </div>
      <div className="pointer-events-none absolute inset-0 opacity-0 transition group-hover:opacity-100">
        <div className="absolute inset-0 bg-gradient-to-br from-[var(--color-primary)]/10 via-transparent to-[var(--color-accent)]/10" />
      </div>
    </div>
  );
}
