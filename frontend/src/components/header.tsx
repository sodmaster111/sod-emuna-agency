export default function Header() {
  return (
    <div className="flex flex-col gap-2 rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl md:flex-row md:items-center md:justify-between">
      <div>
        <p className="text-xs uppercase tracking-[0.25em] text-emerald-300">SOD Command Center</p>
        <h1 className="text-3xl font-bold text-white">Digital Sanhedrin Control Room</h1>
        <p className="text-sm text-slate-400">Monitor council deliberations and dispatch directives to the CEO agent.</p>
      </div>
      <div className="flex items-center gap-3">
        <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-300 ring-1 ring-emerald-500/40">
          FastAPI @ 8000
        </span>
        <span className="rounded-full bg-blue-500/10 px-3 py-1 text-xs font-semibold text-blue-300 ring-1 ring-blue-500/40">
          Next.js 14
        </span>
      </div>
    </div>
  );
}
