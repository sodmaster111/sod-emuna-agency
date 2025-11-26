import Link from "next/link";

import type { Lang } from "@/app/content/updates";

type PublicHeaderProps = {
  lang: Lang;
  title: string;
  nav: {
    home: string;
    updates: string;
    login: string;
  };
};

export default function PublicHeader({ lang, title, nav }: PublicHeaderProps) {
  const withLang = (href: string) => (lang === "he" ? href : `${href}?lang=${lang}`);

  const navItems = [
    { href: withLang("/"), label: nav.home },
    { href: withLang("/updates"), label: nav.updates },
    { href: withLang("/login"), label: nav.login },
  ];

  return (
    <header className="border-b border-slate-800/60 bg-slate-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
        <Link href={withLang("/")} className="text-lg font-semibold text-white">
          {title}
        </Link>
        <nav className="flex items-center gap-6 text-sm font-medium text-slate-200">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href} className="transition hover:text-emerald-300">
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
