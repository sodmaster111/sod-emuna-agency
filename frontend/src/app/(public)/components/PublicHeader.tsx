import Link from "next/link";

import { Container } from "./Container";

export function PublicHeader() {
  return (
    <header className="border-b border-[var(--color-border)]/70 bg-[var(--color-surface)]/80 backdrop-blur">
      <Container className="flex flex-col gap-3 py-6 sm:flex-row sm:items-center sm:justify-between">
        <Link href="/" className="text-xl font-semibold text-[var(--color-text)]">
          SOD Autonomous
        </Link>
        <nav className="flex flex-wrap items-center gap-4 text-sm text-[var(--color-muted)]">
          <Link className="transition hover:text-[var(--color-text)]" href="/donate">
            Donate
          </Link>
          <Link className="transition hover:text-[var(--color-text)]" href="/dashboard">
            Command Center
          </Link>
          <Link className="transition hover:text-[var(--color-text)]" href="/login">
            Sign in
          </Link>
        </nav>
      </Container>
    </header>
  );
}
