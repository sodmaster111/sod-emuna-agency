import { ButtonHTMLAttributes } from "react";

import { ArrowUpRight } from "lucide-react";

interface HeroSectionProps {
  eyebrow?: string;
  title: string;
  description?: string;
  ctaLabel?: string;
  ctaHref?: string;
  secondaryCta?: {
    label: string;
    href: string;
  };
}

export function HeroSection({
  eyebrow,
  title,
  description,
  ctaHref,
  ctaLabel = "Engage",
  secondaryCta,
}: HeroSectionProps) {
  return (
    <section className="relative overflow-hidden rounded-3xl border border-[var(--color-border)] bg-gradient-to-br from-[var(--color-surface)] via-[var(--color-card)] to-[var(--color-surface)] p-10 shadow-xl">
      <div className="relative z-10 max-w-3xl space-y-6">
        {eyebrow ? (
          <span className="inline-flex items-center gap-2 rounded-full border border-[var(--color-border)] bg-black/20 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-[var(--color-muted)]">
            <span className="h-2 w-2 rounded-full bg-[var(--color-accent)]" />
            {eyebrow}
          </span>
        ) : null}
        <h1 className="text-4xl font-bold leading-tight text-[var(--color-text)] md:text-5xl">
          {title}
        </h1>
        {description ? (
          <p className="text-lg leading-relaxed text-[var(--color-muted)] md:text-xl">{description}</p>
        ) : null}
        <div className="flex flex-wrap gap-4">
          <CTAButton href={ctaHref}>{ctaLabel}</CTAButton>
          {secondaryCta ? (
            <a
              className="inline-flex items-center gap-2 rounded-xl border border-[var(--color-border)] px-4 py-2 text-sm font-semibold text-[var(--color-text)] transition hover:-translate-y-0.5 hover:border-[var(--color-accent)]"
              href={secondaryCta.href}
            >
              {secondaryCta.label}
            </a>
          ) : null}
        </div>
      </div>
      <div className="pointer-events-none absolute inset-0 opacity-70 blur-3xl">
        <div className="absolute -right-24 -top-24 h-64 w-64 rounded-full bg-[var(--color-accent)]/30" />
        <div className="absolute -bottom-24 -left-24 h-72 w-72 rounded-full bg-[var(--color-primary)]/25" />
      </div>
    </section>
  );
}

function CTAButton({ href, children, ...props }: ButtonHTMLAttributes<HTMLAnchorElement>) {
  if (href) {
    return (
      <a
        {...props}
        className="inline-flex items-center gap-2 rounded-xl bg-[var(--color-primary)] px-5 py-3 text-sm font-semibold text-black shadow-lg shadow-[var(--color-primary)]/20 transition hover:-translate-y-0.5 hover:shadow-xl"
        href={href}
      >
        {children}
        <ArrowUpRight className="h-4 w-4" />
      </a>
    );
  }

  return (
    <span className="inline-flex items-center gap-2 rounded-xl bg-[var(--color-primary)] px-5 py-3 text-sm font-semibold text-black shadow-lg shadow-[var(--color-primary)]/20">
      {children}
      <ArrowUpRight className="h-4 w-4" />
    </span>
  );
}
