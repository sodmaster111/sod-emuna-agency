import Link from "next/link";

import { updates, type Lang } from "@/app/content/updates";

type UpdatesListProps = {
  lang: Lang;
};

const DATE_LOCALES: Record<Lang, Intl.LocalesArgument> = {
  he: "he-IL",
  ru: "ru-RU",
};

export default function UpdatesList({ lang }: UpdatesListProps) {
  return (
    <div className="space-y-4">
      {updates.map((update) => {
        const title = lang === "ru" ? update.title_ru ?? update.title_he : update.title_he;
        const excerpt = lang === "ru" ? update.excerpt_ru ?? update.excerpt_he : update.excerpt_he;
        const readMoreLabel = lang === "ru" ? "Читать обновление" : "לקריאה נוספת";
        const formattedDate = new Intl.DateTimeFormat(DATE_LOCALES[lang], {
          year: "numeric",
          month: "short",
          day: "numeric",
        }).format(new Date(update.date));

        return (
          <article
            key={update.slug}
            className="rounded-2xl border border-slate-800/80 bg-slate-900/70 p-6 shadow-lg shadow-emerald-500/5"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="space-y-2">
                <h2 className="text-xl font-semibold text-white">{title}</h2>
                <p className="text-sm text-slate-300">{excerpt}</p>
              </div>
              <time className="whitespace-nowrap text-xs uppercase tracking-wide text-emerald-200/80" dateTime={update.date}>
                {formattedDate}
              </time>
            </div>
            <div className="mt-4">
              <Link
                href="#"
                className="inline-flex items-center gap-2 text-sm font-semibold text-emerald-300 transition hover:text-emerald-200"
              >
                {readMoreLabel}
                <span aria-hidden>→</span>
              </Link>
            </div>
          </article>
        );
      })}
    </div>
  );
}
