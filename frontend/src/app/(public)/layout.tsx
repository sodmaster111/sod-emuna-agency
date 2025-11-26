"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";

import Header from "@/app/components/public/Header";
import { defaultLang, Lang, languages } from "@/app/i18n/config";
import { Dictionary, getDictionary } from "@/app/i18n/getDictionary";
import he from "@/app/i18n/dictionaries/he.json";

type I18nContextValue = {
  lang: Lang;
  dictionary: Dictionary;
};

const I18nContext = createContext<I18nContextValue>({
  lang: defaultLang,
  dictionary: he,
});

export function useI18n() {
  return useContext(I18nContext);
}

export default function PublicLayout({ children }: { children: React.ReactNode }) {
  const searchParams = useSearchParams();
  const langParam = searchParams.get("lang");
  const lang = useMemo(
    () => (languages.includes(langParam as Lang) ? (langParam as Lang) : defaultLang),
    [langParam],
  );

  const [dictionary, setDictionary] = useState<Dictionary>(he);

  useEffect(() => {
    getDictionary(lang).then(setDictionary);
  }, [lang]);

  return (
    <I18nContext.Provider value={{ lang, dictionary }}>
      <div className="min-h-screen bg-slate-950 text-white">
        <Header lang={lang} dictionary={dictionary} />
        <main>{children}</main>
      </div>
    </I18nContext.Provider>
  );
}
