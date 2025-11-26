"use client";

import type { ReactNode } from "react";
import { useMemo, useState } from "react";
import { ArrowRight, Mail, UserRound, Wallet2 } from "lucide-react";

import type { PublicDictionary } from "@/app/(public)/i18n/dictionaries";

interface DonationFormProps {
  copy: PublicDictionary["donate"];
}

export function DonationForm({ copy }: DonationFormProps) {
  const [amount, setAmount] = useState("150");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [note, setNote] = useState("Supporting the public treasury");
  const [submitted, setSubmitted] = useState(false);

  const tonAddress = useMemo(() => "EQC-AGENT-AI-TREASURY-00", []);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitted(true);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-6 rounded-3xl border border-[var(--color-border)] bg-[var(--color-card)]/80 p-8 shadow-xl shadow-black/20"
    >
      <div className="grid gap-4 md:grid-cols-2">
        <Field icon={<Wallet2 className="h-4 w-4" />} label={copy.amount_label}>
          <input
            type="number"
            value={amount}
            onChange={(event) => setAmount(event.target.value)}
            className="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]/70 px-4 py-3 text-[var(--color-text)] focus:border-[var(--color-primary)] focus:outline-none"
          />
        </Field>
        <Field icon={<ArrowRight className="h-4 w-4" />} label="Preferred memo">
          <input
            type="text"
            value={note}
            onChange={(event) => setNote(event.target.value)}
            className="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]/70 px-4 py-3 text-[var(--color-text)] focus:border-[var(--color-primary)] focus:outline-none"
          />
        </Field>
      </div>

      <div className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)]/70 p-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-[var(--color-text)]">
          <Wallet2 className="h-4 w-4" />
          <span>Treasury Address</span>
        </div>
        <p className="mt-2 font-mono text-[var(--color-muted)]">{tonAddress}</p>
      </div>

      <div className="space-y-4">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[var(--color-muted)]">{copy.contact_title}</p>
        <div className="grid gap-4 md:grid-cols-2">
          <Field icon={<UserRound className="h-4 w-4" />} label="Name">
            <input
              type="text"
              value={name}
              onChange={(event) => setName(event.target.value)}
              className="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]/70 px-4 py-3 text-[var(--color-text)] focus:border-[var(--color-primary)] focus:outline-none"
            />
          </Field>
          <Field icon={<Mail className="h-4 w-4" />} label="Email">
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]/70 px-4 py-3 text-[var(--color-text)] focus:border-[var(--color-primary)] focus:outline-none"
            />
          </Field>
        </div>
      </div>

      {submitted ? (
        <div className="rounded-2xl border border-[var(--color-primary)]/50 bg-[var(--color-primary)]/10 px-4 py-3 text-sm text-[var(--color-text)]">
          {copy.submit_success}
        </div>
      ) : null}

      <button
        type="submit"
        className="group inline-flex w-full items-center justify-between gap-2 rounded-xl bg-[var(--color-primary)] px-4 py-3 text-sm font-semibold text-black shadow-lg shadow-[var(--color-primary)]/20 transition hover:-translate-y-0.5"
      >
        <span>{submitted ? "Pledge recorded" : "Authorize TON transfer"}</span>
        <ArrowRight className="h-4 w-4 transition group-hover:translate-x-1" />
      </button>
    </form>
  );
}

function Field({ label, icon, children }: { label: string; icon?: ReactNode; children: ReactNode }) {
  return (
    <label className="block space-y-2 text-sm text-[var(--color-text)]">
      <span className="flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-[var(--color-muted)]">
        {icon}
        {label}
      </span>
      {children}
    </label>
  );
}
