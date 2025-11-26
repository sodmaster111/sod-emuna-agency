"use client";

import { useEffect, useState } from "react";
import { Loader2, MoonStar } from "lucide-react";

import type { DayInfo } from "@/app/lib/ritual_api";
import { fetchDayInfo } from "@/app/lib/ritual_api";

const DAY_TYPE_LABELS: Record<string, string> = {
  shabbat: "שבת",
  weekday: "חול",
  rosh_chodesh: "ראש חודש",
};

const DAY_TYPE_SUGGESTIONS: Record<string, string> = {
  shabbat: "מנוחה, תפילה ודברי תורה.",
  weekday: "המשך בעשייה עם רגע של כוונה.",
  rosh_chodesh: "זמן להתחדשות וברכה.",
};

export function DailyWidget({ lang }: { lang?: string }) {
  const [dayInfo, setDayInfo] = useState<DayInfo | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const loadDayInfo = async () => {
      setIsLoading(true);
      try {
        const data = await fetchDayInfo(lang);
        if (!isMounted) return;
        setDayInfo(data);
        setError(null);
      } catch (err) {
        if (!isMounted) return;
        setError("המידע אינו זמין כעת.");
        setDayInfo(null);
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadDayInfo();
    return () => {
      isMounted = false;
    };
  }, [lang]);

  const dayTypeKey = dayInfo?.day_type?.toLowerCase();
  const dayTypeLabel = dayTypeKey ? DAY_TYPE_LABELS[dayTypeKey] ?? dayInfo?.day_type : null;
  const suggestion = dayTypeKey ? DAY_TYPE_SUGGESTIONS[dayTypeKey] : null;

  return (
    <div className="relative overflow-hidden rounded-3xl border border-slate-800 bg-gradient-to-br from-slate-900/80 via-slate-900/40 to-slate-900/80 p-6 shadow-xl shadow-emerald-500/10">
      <div className="absolute -left-6 -top-6 h-24 w-24 rounded-full bg-emerald-500/10 blur-3xl" />
      <div className="absolute -bottom-10 -right-4 h-32 w-32 rounded-full bg-indigo-500/10 blur-3xl" />

      <div className="relative flex items-start justify-between gap-4">
        <div className="space-y-1">
          <p className="text-xs uppercase tracking-[0.3em] text-emerald-300">היום בלוח העברי</p>
          <h3 className="text-xl font-semibold text-white">מיקוד רוחני יומי</h3>
        </div>
        <span className="inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-emerald-500/10 text-emerald-200 ring-1 ring-emerald-500/30">
          <MoonStar className="h-5 w-5" />
        </span>
      </div>

      <div className="relative mt-4 space-y-3 text-sm text-slate-200">
        {isLoading ? (
          <div className="flex items-center gap-2 text-slate-300">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>טוען נתוני יום…</span>
          </div>
        ) : error ? (
          <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-amber-100">{error}</div>
        ) : dayInfo ? (
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2 text-lg font-semibold text-white">
              <span>{dayInfo.jewish_date_str}</span>
              {dayInfo.parsha ? <span className="text-emerald-300">• {dayInfo.parsha}</span> : null}
            </div>

            {dayTypeLabel ? (
              <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-100">
                {dayTypeLabel}
              </div>
            ) : null}

            {suggestion ? (
              <p className="text-slate-300">{suggestion}</p>
            ) : (
              <p className="text-slate-400">התעדכנו בלוח היום ושמרו על קצב נשימה רגוע.</p>
            )}
          </div>
        ) : (
          <p className="text-slate-400">המידע אינו זמין כעת.</p>
        )}
      </div>
    </div>
  );
}
