"use client";

import { useMemo, useState } from "react";

import { ArrowRight, Wallet } from "lucide-react";

interface DonationFormProps {
  title?: string;
  description?: string;
  ctaLabel?: string;
}

export function DonationForm({
  title = "Support the AI Treasury",
  description = "Authorize TON contributions to accelerate the SOD roadmap.",
  ctaLabel = "Authorize TON Transfer",
}: DonationFormProps) {
  const [connected, setConnected] = useState(false);
  const [amount, setAmount] = useState("100");
  const [message, setMessage] = useState("For the Board");

  const tonAddress = useMemo(() => "EQC-AGENT-AI-TREASURY-00", []);

  return (
    <section className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-card)] p-6 shadow-sm">
      <header className="mb-4 flex items-center justify-between gap-3">
        <div className="space-y-1">
          <p className="text-xs uppercase tracking-[0.25em] text-[var(--color-muted)]">Donation</p>
          <h3 className="text-lg font-semibold text-[var(--color-text)]">{title}</h3>
          <p className="text-sm text-[var(--color-muted)]">{description}</p>
        </div>
        <span className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold ${connected ? "bg-green-500/15 text-green-300" : "bg-[var(--color-accent)]/15 text-[var(--color-accent)]"}`}>
          <span className={`h-2 w-2 rounded-full ${connected ? "bg-green-400" : "bg-[var(--color-accent)]"}`} />
          {connected ? "Wallet linked" : "TON Connect"}
        </span>
      </header>

      <div className="space-y-4">
        <div className="grid gap-3 md:grid-cols-2">
          <Field label="Amount (TON)">
            <input
              type="number"
              value={amount}
              onChange={(event) => setAmount(event.target.value)}
              className="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]/70 px-4 py-3 text-[var(--color-text)] focus:border-[var(--color-primary)] focus:outline-none"
            />
          </Field>
          <Field label="Memo">
            <input
              type="text"
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              className="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]/70 px-4 py-3 text-[var(--color-text)] focus:border-[var(--color-primary)] focus:outline-none"
            />
          </Field>
        </div>

        <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]/70 p-4 text-sm text-[var(--color-muted)]">
          <p className="flex items-center gap-2 text-[var(--color-text)]">
            <Wallet className="h-4 w-4" />
            Treasury Address
          </p>
          <p className="mt-2 font-mono text-[var(--color-text)]">{tonAddress}</p>
        </div>

        <button
          onClick={() => setConnected((value) => !value)}
          className="group inline-flex w-full items-center justify-between gap-2 rounded-xl bg-[var(--color-primary)] px-4 py-3 text-sm font-semibold text-black shadow-lg shadow-[var(--color-primary)]/20 transition hover:-translate-y-0.5"
        >
          <span>{connected ? "Ready to authorize" : ctaLabel}</span>
          <ArrowRight className="h-4 w-4 transition group-hover:translate-x-1" />
        </button>
      </div>
    </section>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block space-y-2 text-sm text-[var(--color-text)]">
      <span className="text-xs uppercase tracking-[0.2em] text-[var(--color-muted)]">{label}</span>
      {children}
    </label>
  );
}
