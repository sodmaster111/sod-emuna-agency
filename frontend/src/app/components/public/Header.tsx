"use client";

import Link from "next/link";

import { Lang } from "@/app/i18n/config";
import { Dictionary } from "@/app/i18n/getDictionary";

import LanguageSwitcher from "./LanguageSwitcher";

type HeaderProps = {
  lang: Lang;
  dictionary: Dictionary;
};

export default function Header({ lang, dictionary }: HeaderProps) {
  return (
    <header className="sticky top-0 z-20 border-b border-white/5 bg-slate-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <Link href="/" className="text-lg font-semibold text-emerald-200">
          {dictionary.common.brand}
        </Link>
        <nav className="hidden items-center gap-6 text-sm text-white/80 sm:flex">
          <Link href="#home" className="hover:text-white">
            {dictionary.nav.home}
          </Link>
          <Link href="#mission" className="hover:text-white">
            {dictionary.nav.mission}
          </Link>
          <Link href="#about" className="hover:text-white">
            {dictionary.nav.about}
          </Link>
          <Link href="#contact" className="hover:text-white">
            {dictionary.nav.contact}
          </Link>
          <Link href="#donate" className="hover:text-white">
            {dictionary.nav.donate}
          </Link>
        </nav>
        <LanguageSwitcher currentLang={lang} />
      </div>
    </header>
  );
}
