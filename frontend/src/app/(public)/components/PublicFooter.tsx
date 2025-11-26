import Link from "next/link";

import { Container } from "./Container";

export function PublicFooter() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-[var(--color-border)]/60 bg-[var(--color-surface)]/70">
      <Container className="flex flex-col gap-4 py-6 text-sm text-[var(--color-muted)] sm:flex-row sm:items-center sm:justify-between">
        <p className="text-[var(--color-muted)]">© {year} SOD Autonomous Corporation</p>
        <div className="flex flex-wrap gap-4">
          <Link className="transition hover:text-[var(--color-text)]" href="/donate">
            Donate
          </Link>
          <Link className="transition hover:text-[var(--color-text)]" href="/dashboard">
            Dashboard
          </Link>
          <Link className="transition hover:text-[var(--color-text)]" href="mailto:finance@sod.agency">
            finance@sod.agency
          </Link>
        </div>
      </Container>
    </footer>
  );
}
