import Image from "next/image";

import { Sparkles } from "lucide-react";

interface NftItem {
  id?: string | number;
  title: string;
  image?: string;
  description?: string;
  badge?: string;
}

interface NftGridProps {
  title?: string;
  subtitle?: string;
  items?: NftItem[];
}

export function NftGrid({ title = "AI Minted Intelligence", subtitle, items = [] }: NftGridProps) {
  return (
    <section className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-card)] p-6 shadow-sm">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-[var(--color-muted)]">NFT grid</p>
          <h3 className="text-xl font-semibold text-[var(--color-text)]">{title}</h3>
          {subtitle ? <p className="text-sm text-[var(--color-muted)]">{subtitle}</p> : null}
        </div>
        <span className="inline-flex items-center gap-2 rounded-full bg-[var(--color-accent)]/15 px-3 py-1 text-xs font-semibold text-[var(--color-accent)]">
          <Sparkles className="h-4 w-4" />
          live mint
        </span>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {items.length === 0 ? (
          <div className="col-span-full rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]/70 p-6 text-center text-[var(--color-muted)]">
            Content pipeline is warming up...
          </div>
        ) : (
          items.map((item, idx) => (
            <article
              key={item.id ?? idx}
              className="group overflow-hidden rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]/80 shadow-sm transition hover:-translate-y-0.5 hover:border-[var(--color-primary)]/60"
            >
              <div className="relative h-40 w-full bg-gradient-to-br from-[var(--color-primary)]/20 via-transparent to-[var(--color-accent)]/20">
                {item.image ? (
                  <Image
                    src={item.image}
                    alt={item.title}
                    fill
                    className="object-cover transition duration-700 group-hover:scale-105"
                  />
                ) : null}
                {item.badge ? (
                  <span className="absolute left-3 top-3 rounded-full bg-black/60 px-3 py-1 text-xs font-semibold text-[var(--color-text)]">
                    {item.badge}
                  </span>
                ) : null}
              </div>
              <div className="space-y-2 p-4">
                <h4 className="text-lg font-semibold text-[var(--color-text)]">{item.title}</h4>
                {item.description ? (
                  <p className="text-sm leading-relaxed text-[var(--color-muted)]">{item.description}</p>
                ) : null}
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
