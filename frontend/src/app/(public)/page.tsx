"use client";

import { useI18n } from "./layout";

export default function PublicHomePage() {
  const { dictionary } = useI18n();

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-20 px-6 py-12">
      <section id="home" className="space-y-6 rounded-3xl border border-white/10 bg-slate-900/60 p-10 shadow-2xl shadow-emerald-500/10">
        <div className="space-y-3">
          <p className="text-sm uppercase tracking-[0.3em] text-emerald-300">{dictionary.common.brand}</p>
          <h1 className="text-4xl font-bold leading-tight sm:text-5xl">{dictionary.home.hero_title}</h1>
          <p className="max-w-3xl text-lg text-slate-200">{dictionary.home.hero_subtitle}</p>
        </div>
        <div className="flex flex-wrap items-center gap-4">
          <a
            href="#mission"
            className="rounded-full bg-emerald-400 px-6 py-3 text-sm font-semibold text-emerald-950 shadow-lg shadow-emerald-500/30 transition hover:bg-emerald-300"
          >
            {dictionary.home.cta_join}
          </a>
          <a
            href="#donate"
            className="rounded-full border border-white/20 px-6 py-3 text-sm font-semibold text-white/90 transition hover:border-emerald-300 hover:text-emerald-200"
          >
            {dictionary.home.cta_donate}
          </a>
        </div>
      </section>

      <section id="mission" className="grid gap-6 rounded-2xl border border-white/10 bg-slate-900/40 p-8 sm:grid-cols-2">
        <div>
          <h2 className="text-2xl font-semibold text-white">{dictionary.nav.mission}</h2>
          <p className="mt-3 text-slate-200">
            אנחנו מתמקדים בליווי אישי, שמירה על תחושת בית ובניית מערכות סיוע שמכבדות כל משפחה. יחד אנו יוצרים
            קהילה שפועלת במהירות ובחמלה כשהכי צריך.
          </p>
        </div>
        <div className="rounded-xl border border-emerald-400/20 bg-emerald-500/10 p-5 text-emerald-50">
          <p className="text-sm uppercase tracking-wide text-emerald-200/80">{dictionary.nav.donate}</p>
          <p className="mt-2 text-lg font-semibold">משאבים שמגיעים ישירות לשטח</p>
          <p className="mt-2 text-sm text-emerald-50/80">
            כל תרומה מחזקת את מערך הסיוע, מאפשרת התארגנות מהירה בשעת חירום ומממנת פעולות קהילה שמשרות ביטחון ורוגע.
          </p>
        </div>
      </section>

      <section
        id="about"
        className="grid gap-6 rounded-2xl border border-white/10 bg-slate-900/40 p-8 sm:grid-cols-2 sm:items-center"
      >
        <div className="space-y-3">
          <h2 className="text-2xl font-semibold text-white">{dictionary.nav.about}</h2>
          <p className="text-slate-200">
            המנהיגים, המתנדבים והמשפחות שלנו שומרים על עקרונות של שקיפות, שותפות ואחריות. אנו פועלים בשטח,
            מחברים בין מקבלי החלטות לבין הקהילה ומוודאים שלכל קול יש מקום.
          </p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-emerald-500/10 to-cyan-500/10 p-6 text-white">
          <p className="text-sm uppercase tracking-wide text-emerald-200">קהילה מחוברת</p>
          <ul className="mt-3 space-y-2 text-sm text-white/80">
            <li>🟢 מפגשי חוסן והדרכות חירום.</li>
            <li>🟢 צוותי שטח שמזהים צרכים בזמן אמת.</li>
            <li>🟢 תיאום עם רשות מקומית וארגוני סיוע.</li>
          </ul>
        </div>
      </section>

      <section
        id="contact"
        className="grid gap-6 rounded-2xl border border-white/10 bg-slate-900/40 p-8 sm:grid-cols-2 sm:items-center"
      >
        <div>
          <h2 className="text-2xl font-semibold text-white">{dictionary.nav.contact}</h2>
          <p className="mt-2 text-slate-200">
            כדי להצטרף, להתנדב או לדווח על צורך דחוף, מלאו את פרטיכם וניצור קשר עם מענה מותאם.
          </p>
          <form className="mt-6 space-y-4">
            <input
              type="text"
              placeholder="שם מלא"
              className="w-full rounded-lg border border-white/10 bg-slate-950/60 px-4 py-3 text-sm focus:border-emerald-300 focus:outline-none"
            />
            <input
              type="email"
              placeholder="דוא״ל"
              className="w-full rounded-lg border border-white/10 bg-slate-950/60 px-4 py-3 text-sm focus:border-emerald-300 focus:outline-none"
            />
            <button
              type="submit"
              className="w-full rounded-lg bg-emerald-400 px-4 py-3 text-sm font-semibold text-emerald-950 transition hover:bg-emerald-300"
            >
              שלחו הודעה
            </button>
          </form>
        </div>
        <div className="space-y-3 rounded-2xl border border-white/10 bg-slate-950/60 p-6">
          <p className="text-sm uppercase tracking-wide text-emerald-200">{dictionary.nav.home}</p>
          <p className="text-lg font-semibold text-white">קו חירום 24/7</p>
          <p className="text-sm text-white/80">דיווחים אנונימיים, חיבור מיידי לצוותי סיוע ומידע מאומת מהשטח.</p>
        </div>
      </section>

      <section id="donate" className="rounded-2xl border border-emerald-400/30 bg-emerald-500/10 p-8 text-white">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm uppercase tracking-wide text-emerald-200">{dictionary.nav.donate}</p>
            <h3 className="text-2xl font-semibold">{dictionary.home.cta_donate}</h3>
            <p className="text-sm text-white/80">
              תרומה חד-פעמית או חודשית מאפשרת לנו להגיב מהר יותר, לשמור על המלאי החיוני ולהעניק תמיכה נפשית ולוגיסטית.
            </p>
          </div>
          <a
            href="#donate"
            className="inline-flex items-center justify-center rounded-full bg-white px-6 py-3 text-sm font-semibold text-emerald-900 shadow-lg shadow-emerald-500/30 transition hover:bg-emerald-100"
          >
            {dictionary.nav.donate}
          </a>
        </div>
      </section>
    </div>
  );
}
