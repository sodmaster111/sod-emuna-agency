import type { ReactNode } from "react";

import "@/app/globals.css";

import { PublicFooter } from "./components/PublicFooter";
import { PublicHeader } from "./components/PublicHeader";

export default function PublicLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-[var(--color-bg)] text-[var(--color-text)]">
      <PublicHeader />
      <main>{children}</main>
      <PublicFooter />
    </div>
  );
}
