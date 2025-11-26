import type { ReactNode } from "react";

import Link from "next/link";
import { Mail, MessageCircle, Send } from "lucide-react";

interface JoinDictionary {
  join: {
    telegram_title: string;
    telegram_description: string;
    whatsapp_title: string;
    whatsapp_description: string;
    email_title?: string;
    email_description?: string;
  };
}

interface JoinCardsProps {
  dict: JoinDictionary;
}

interface JoinCardItem {
  title: string;
  description: string;
  href: string;
  cta: string;
  icon: ReactNode;
}

export function JoinCards({ dict }: JoinCardsProps) {
  const cards: JoinCardItem[] = [
    {
      title: dict.join.telegram_title,
      description: dict.join.telegram_description,
      href: "https://t.me/Sodmaster",
      cta: "Open Telegram",
      icon: <Send className="h-5 w-5" />,
    },
    {
      title: dict.join.whatsapp_title,
      description: dict.join.whatsapp_description,
      href: "https://wa.me/",
      cta: "Open WhatsApp",
      icon: <MessageCircle className="h-5 w-5" />,
    },
  ];

  if (dict.join.email_title && dict.join.email_description) {
    cards.push({
      title: dict.join.email_title,
      description: dict.join.email_description,
      href: "mailto:community@sodmaster.online",
      cta: "Email the team",
      icon: <Mail className="h-5 w-5" />,
    });
  }

  return (
    <div className="grid gap-6 md:grid-cols-3">
      {cards.map((card) => (
        <div
          key={card.title}
          className="flex h-full flex-col rounded-2xl border border-white/10 bg-slate-900/70 p-6 shadow-xl shadow-black/20"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center justify-center rounded-xl bg-emerald-500/10 p-2 text-emerald-300">
              {card.icon}
            </div>
            <span className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-200/80">Live</span>
          </div>

          <div className="mt-4 space-y-2">
            <h3 className="text-lg font-semibold text-white">{card.title}</h3>
            <p className="text-sm leading-relaxed text-slate-300">{card.description}</p>
          </div>

          <div className="mt-6 flex grow items-end">
            <Link
              className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:-translate-y-0.5 hover:bg-emerald-400"
              href={card.href}
              rel="noreferrer noopener"
              target="_blank"
            >
              {card.cta}
            </Link>
          </div>
        </div>
      ))}
    </div>
  );
}

export default JoinCards;
