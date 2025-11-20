interface KpiCardProps {
  label: string;
  value: string;
  subtext?: string;
}

export default function KpiCard({ label, value, subtext }: KpiCardProps) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-gradient-to-br from-slate-900 to-slate-950 p-4 shadow-lg">
      <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
      <p className="mt-1 text-3xl font-bold text-white">{value}</p>
      {subtext && <p className="mt-1 text-sm text-emerald-300">{subtext}</p>}
    </div>
  );
}
