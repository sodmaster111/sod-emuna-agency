import PublicHeader from "@/app/components/public/PublicHeader";
import UpdatesList from "@/app/components/public/UpdatesList";
import type { Lang } from "@/app/content/updates";

type UpdatesPageProps = {
  searchParams?: { lang?: string };
};

const dictionaries: Record<Lang, { header: { title: string; nav: { home: string; updates: string; login: string } }; updates: { title: string } }> = {
  he: {
    header: {
      title: "SOD Autonomous Agency",
      nav: {
        home: "בית",
        updates: "עדכונים",
        login: "כניסה",
      },
    },
    updates: {
      title: "עדכונים אחרונים",
    },
  },
  ru: {
    header: {
      title: "SOD Autonomous Agency",
      nav: {
        home: "Главная",
        updates: "Обновления",
        login: "Вход",
      },
    },
    updates: {
      title: "Последние обновления",
    },
  },
};

const resolveLang = (rawLang?: string): Lang => {
  return rawLang === "ru" ? "ru" : "he";
};

export default function UpdatesPage({ searchParams }: UpdatesPageProps) {
  const lang = resolveLang(searchParams?.lang);
  const dict = dictionaries[lang];

  return (
    <main className="min-h-screen bg-slate-950 text-slate-50">
      <PublicHeader lang={lang} title={dict.header.title} nav={dict.header.nav} />
      <section className="mx-auto max-w-5xl space-y-6 px-6 py-12">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.25em] text-emerald-300">{dict.header.title}</p>
          <h1 className="text-3xl font-bold sm:text-4xl">{dict.updates.title}</h1>
          <p className="max-w-3xl text-sm text-slate-300">
            אוסף קצר של שדרוגים והודעות מהצוות. נמשיך להוסיף יכולות ולקשר למערכת תוכן מלאה בהמשך.
          </p>
        </div>
        <UpdatesList lang={lang} />
      </section>
    </main>
  );
}
