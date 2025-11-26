import type { Metadata } from "next";

import { HowItWorks } from "@/app/components/public/HowItWorks";
import { DailyWidget } from "@/app/components/public/DailyWidget";
import { Container, Section } from "@/app/components/public/layout";
import { getDictionary } from "@/app/dictionaries";

export const metadata: Metadata = {
  title: "SOD | How it works",
  description: "סיפור פשוט על הסוכנים, הקהילה והאוצר בטון שמניעים את SOD.",
};

export default function PublicHomePage() {
  const dictionary = getDictionary("he");

  return (
    <main className="bg-slate-950 text-slate-50">
      <Section className="bg-gradient-to-b from-slate-900/70 via-slate-950 to-slate-950">
        <Container className="grid gap-8 lg:grid-cols-[1.2fr,0.8fr] lg:items-center">
          <div className="space-y-6">
            <p className="text-sm uppercase tracking-[0.35em] text-emerald-300">Story of the Day</p>
            <h1 className="text-4xl font-bold leading-tight text-white sm:text-5xl">
              חיבור בין בינה, קהילה ואוצר מבוזר
            </h1>
            <p className="max-w-2xl text-lg leading-relaxed text-slate-200">
              הסיפור של SOD פשוט: סוכני AMAC מקשיבים, הקהילה מחוברת בערוצים, והאוצר בטון מממן משימות ותומך בתורמים עם
              קמעות ותגמולים.
            </p>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-2xl border border-white/10 bg-slate-900/60 p-4 shadow-inner shadow-black/30">
                <p className="text-sm uppercase tracking-[0.2em] text-emerald-200">Agents</p>
                <p className="text-base text-slate-100">
                  החלטות חכמות, ביצוע מהיר ורגישות קהילתית בכל פעולה.
                </p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-slate-900/60 p-4 shadow-inner shadow-black/30">
                <p className="text-sm uppercase tracking-[0.2em] text-emerald-200">TON Treasury</p>
                <p className="text-base text-slate-100">זרימת תרומות ליעדים ברורים עם שקיפות והוקרה לתומכים.</p>
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-slate-900/60 p-6 shadow-2xl shadow-emerald-500/10">
            <div className="space-y-3">
              <p className="text-xs uppercase tracking-[0.25em] text-emerald-300">AMAC Pulse</p>
              <h2 className="text-2xl font-semibold text-white">זרם פעולות קבוע</h2>
              <p className="text-sm leading-relaxed text-slate-200">
                שגרות, תצפיות ודגשים מגיעים בזמן אמת. כל שלב נבנה כדי לשמור על שקט, ביטחון ותנועה קדימה.
              </p>
            </div>
            <div className="mt-4 space-y-3 divide-y divide-white/5">
              {["הפעלה יומית של סוכנים", "שידורי קהילה", "דוחות אוצר בטון"].map((item) => (
                <div key={item} className="flex items-center justify-between pt-3 first:pt-0">
                  <p className="text-sm text-slate-100">{item}</p>
                  <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-200">פעיל</span>
                </div>
              ))}
            </div>
          </div>
        </Container>
      </Section>

      <DailyWidget />

      <HowItWorks content={dictionary.home} />
    </main>
  );
}
