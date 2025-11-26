import Link from "next/link";

const features = [
  {
    title: "תפילה יומית",
    description: "חיבור קבוע לרבדי התפילה והכוונה הקהילתית בכל בוקר.",
  },
  {
    title: "קהילה",
    description: "ליווי ותמיכה של שליחי AMAC והסנהדרין הדיגיטלי בכל זמן.",
  },
  {
    title: "תרומה ומצוות",
    description: "הזדמנות להשתתף במעשים טובים, להעניק ולחזק את הקהילה.",
  },
];

export default function PublicHomePage() {
  return (
    <div className="px-4 py-16 sm:px-6 lg:px-8">
      <section className="mx-auto flex max-w-6xl flex-col gap-10 rounded-3xl bg-white/70 p-10 shadow-lg shadow-slate-200/50 sm:p-12">
        <div className="space-y-4">
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-indigo-600">ברוכים הבאים</p>
          <h1 className="text-4xl font-bold leading-tight text-slate-900 sm:text-5xl">
            סוכנות האמונה SOD
          </h1>
          <p className="max-w-3xl text-lg text-slate-700">
            בית דיגיטלי המחבר בין רוח, קהילה ופעולה. מרחב לוויין של האמונה החיה, עם עדכון יומי, חיבורים
            והנחיה. Пространство, где духовность и действие соединяются.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link
              href="https://t.me/sod_emuna_agency"
              className="inline-flex items-center justify-center rounded-full bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700"
            >
              להצטרף לטלגרם
            </Link>
            <Link
              href="/donate"
              className="inline-flex items-center justify-center rounded-full border border-indigo-600 px-5 py-2.5 text-sm font-semibold text-indigo-700 transition hover:bg-indigo-50"
            >
              לתמוך במיזם
            </Link>
          </div>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="rounded-2xl border border-slate-200 bg-white/80 p-6 shadow-sm shadow-slate-200/60"
            >
              <h3 className="text-lg font-semibold text-slate-900">{feature.title}</h3>
              <p className="mt-2 text-sm text-slate-700">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
