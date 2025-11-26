import type { PublicDictionary } from "@/app/(public)/i18n/dictionaries";

interface DonationSummaryProps {
  copy: PublicDictionary["donate"];
}

export function DonationSummary({ copy }: DonationSummaryProps) {
  return (
    <div className="mx-auto max-w-3xl space-y-4 text-center">
      <p className="text-lg leading-relaxed text-[var(--color-muted)]">{copy.subtitle}</p>
      <div className="flex flex-wrap justify-center gap-3 text-sm text-[var(--color-muted)]">
        <span className="rounded-full border border-[var(--color-border)] px-3 py-2">Secure TON treasury</span>
        <span className="rounded-full border border-[var(--color-border)] px-3 py-2">Transparent impact updates</span>
        <span className="rounded-full border border-[var(--color-border)] px-3 py-2">Community aligned</span>
      </div>
    </div>
  );
}
