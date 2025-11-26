"use client";

import { useCallback } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

import { Lang, languages } from "@/app/i18n/config";

const labels: Record<Lang, string> = {
  he: "HE",
  ru: "RU",
  en: "EN",
};

export default function LanguageSwitcher({ currentLang }: { currentLang: Lang }) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const handleChange = useCallback(
    (lang: Lang) => {
      const next = new URLSearchParams(searchParams.toString());
      next.set("lang", lang);

      const query = next.toString();
      const destination = query ? `${pathname}?${query}` : pathname;
      router.push(destination);
    },
    [pathname, router, searchParams],
  );

  return (
    <div className="flex items-center gap-2">
      {languages.map((lang) => (
        <button
          key={lang}
          type="button"
          onClick={() => handleChange(lang)}
          className={`rounded-full border px-3 py-1 text-xs font-semibold transition hover:border-emerald-400 hover:text-emerald-200 ${
            lang === currentLang
              ? "border-emerald-400/80 bg-emerald-500/10 text-emerald-200"
              : "border-white/10 bg-white/5 text-white/80"
          }`}
        >
          {labels[lang]}
        </button>
      ))}
    </div>
  );
}
