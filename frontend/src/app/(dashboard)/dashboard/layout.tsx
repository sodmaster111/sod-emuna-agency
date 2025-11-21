import Link from "next/link";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      <header className="border-b border-white/10 bg-slate-900/70 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div>
            <p className="text-xs uppercase tracking-widest text-slate-400">Command Center</p>
            <h1 className="text-xl font-semibold text-white">Nasi Management Console</h1>
          </div>
          <nav className="flex gap-3 text-sm text-slate-200">
            <Link className="rounded-lg px-3 py-2 transition hover:bg-white/5" href="/dashboard">
              Overview
            </Link>
            <Link className="rounded-lg px-3 py-2 transition hover:bg-white/5" href="/dashboard/pinkas">
              Pinkas Logs
            </Link>
            <Link className="rounded-lg px-3 py-2 transition hover:bg-white/5" href="/dashboard/commands">
              Commands
            </Link>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-10">
        <div className="rounded-2xl border border-white/10 bg-slate-900/60 p-8 shadow-xl shadow-black/30">
          {children}
        </div>
      </main>
    </div>
  );
}
