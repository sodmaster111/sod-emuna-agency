import Link from "next/link";
import type { ReactNode } from "react";

function ActionButton({ href, children }: { href: string; children: ReactNode }) {
  return (
    <Link
      href={href}
      className="inline-flex items-center justify-center rounded-xl bg-emerald-500 px-4 py-3 text-sm font-semibold text-slate-950 shadow-lg shadow-emerald-500/20 transition hover:-translate-y-0.5 hover:bg-emerald-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-300"
    >
      {children}
    </Link>
  );
}

export default function PublicNotFound() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-50">
      <div className="mx-auto flex min-h-screen max-w-5xl items-center px-6 py-16">
        <section className="w-full space-y-6 rounded-3xl border border-white/10 bg-slate-900/70 p-10 shadow-2xl shadow-emerald-500/10">
          <p className="text-xs uppercase tracking-[0.3em] text-emerald-300">Navigation</p>
          <div className="space-y-3">
            <h1 className="text-3xl font-bold sm:text-4xl">404 — הדף לא נמצא</h1>
            <p className="text-lg text-slate-200">העמוד שחיפשת אינו זמין כרגע. בדוק את הכתובת או חזור לדף הבית.</p>
            <p className="text-base text-slate-300">Страница временно недоступна или не существует. Проверьте ссылку или вернитесь на главную.</p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row">
            <ActionButton href="/">Back to home</ActionButton>
            <Link
              href="/contact"
              className="inline-flex items-center justify-center rounded-xl border border-emerald-200/40 bg-transparent px-4 py-3 text-sm font-semibold text-emerald-200 transition hover:-translate-y-0.5 hover:bg-emerald-500/10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-300"
            >
              Contact
            </Link>
          </div>
        </section>
      </div>
    </main>
  );
}
