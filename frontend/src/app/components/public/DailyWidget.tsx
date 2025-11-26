import { Container, Section } from "./layout";

export function DailyWidget() {
  return (
    <Section>
      <Container>
        <div className="rounded-3xl border border-white/10 bg-slate-900/50 p-8 shadow-xl shadow-black/30 sm:p-10">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="space-y-2">
              <p className="text-xs uppercase tracking-[0.3em] text-emerald-300">Daily Widget</p>
              <h2 className="text-2xl font-semibold text-white sm:text-3xl">חיבור יומי לערוצים</h2>
              <p className="max-w-2xl text-sm leading-relaxed text-slate-200">
                תוכן קצר ותפילות מגיעים בכל בוקר לערוצי הטלגרם והווטסאפ, כדי שהקהילה תקבל השראה ומיקוד לפני שמתחילים את
                היום.
              </p>
            </div>
            <div className="grid w-full max-w-sm grid-cols-2 gap-3 text-center sm:max-w-xs">
              <div className="rounded-2xl border border-white/10 bg-slate-950/40 p-4">
                <p className="text-3xl font-semibold text-white">24/7</p>
                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">תמיכה</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-slate-950/40 p-4">
                <p className="text-3xl font-semibold text-white">2</p>
                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">ערוצים</p>
              </div>
            </div>
          </div>
        </div>
      </Container>
    </Section>
  );
}
