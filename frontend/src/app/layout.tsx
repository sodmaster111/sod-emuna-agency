import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

import { QueryProvider } from "@/components/providers/query-provider";
import { ThemeInitializer } from "@/components/theme-initializer";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "SOD Public Intelligence",
  description: "Dynamic AI-managed interface for SOD master operations",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-[var(--color-bg)] text-[var(--color-text)]`}>
        <div className="min-h-screen bg-[var(--color-bg)]">
          <QueryProvider>
            <ThemeInitializer />
            <div className="mx-auto max-w-6xl space-y-6 px-4 py-10">
              <header className="space-y-2 text-center">
                <p className="text-xs uppercase tracking-[0.3em] text-[var(--color-muted)]">SOD Corporation</p>
                <h1 className="text-2xl font-semibold text-[var(--color-text)]">
                  AI-directed experience for sodmaster.online
                </h1>
              </header>
              {children}
            </div>
          </QueryProvider>
        </div>
      </body>
    </html>
  );
}
