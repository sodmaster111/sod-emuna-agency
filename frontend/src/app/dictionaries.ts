export type Locale = "en" | "he" | "ru";

export type HomeDictionary = {
  how_it_works_title: string;
  how_it_works_step1_title: string;
  how_it_works_step1_body: string;
  how_it_works_step2_title: string;
  how_it_works_step2_body: string;
  how_it_works_step3_title: string;
  how_it_works_step3_body: string;
  how_it_works_step4_title: string;
  how_it_works_step4_body: string;
};

export type Dictionary = {
  home: HomeDictionary;
};

const dictionaries: Record<Locale, Dictionary> = {
  he: {
    home: {
      how_it_works_title: "איך SOD עובד",
      how_it_works_step1_title: "הסוכנים",
      // TODO: לתרגם לרוסית/אנגלית במידת הצורך
      how_it_works_step1_body:
        "סוכני AMAC מקשיבים לצרכים, מחברים ידע, ומייצרים פעולות שעוזרות לקהילה.",
      how_it_works_step2_title: "הקהילה",
      how_it_works_step2_body:
        "התכנים היומיים והתפילות נשלחים בערוצים כדי שכל אחד יקבל השראה ותמיכה בזמן.",
      how_it_works_step3_title: "האוצר",
      how_it_works_step3_body: "תרומות ב‑TON נכנסות לקרן שמממנת משימות ופעולות שטח.",
      how_it_works_step4_title: "תגמולים",
      how_it_works_step4_body: "תומכים מקבלים קמעות מיוחדים ואסימונים עתידיים כהוקרה ושייכות.",
    },
  },
  en: {
    home: {
      how_it_works_title: "How SOD Works",
      how_it_works_step1_title: "Agents",
      how_it_works_step1_body:
        "AMAC agents listen to needs, connect knowledge, and trigger helpful actions for the community.",
      how_it_works_step2_title: "Community",
      how_it_works_step2_body:
        "Daily teachings and tefillot are shared through the channels so everyone receives encouragement when they need it.",
      how_it_works_step3_title: "Treasury",
      how_it_works_step3_body: "TON donations flow into a mission fund that powers on-the-ground initiatives.",
      how_it_works_step4_title: "Rewards",
      how_it_works_step4_body: "Supporters receive special amulets and future token credits as a sign of gratitude and belonging.",
    },
  },
  ru: {
    home: {
      how_it_works_title: "Как работает SOD",
      how_it_works_step1_title: "Агенты",
      how_it_works_step1_body:
        "Агенты AMAC прислушиваются к запросам, собирают знания и запускают действия на благо сообщества.",
      how_it_works_step2_title: "Сообщество",
      how_it_works_step2_body:
        "Ежедневные материалы и молитвы отправляются в каналы, чтобы каждый получал поддержку вовремя.",
      how_it_works_step3_title: "Казна",
      how_it_works_step3_body: "Пожертвования в TON поступают в фонд миссий и финансируют реальные действия.",
      how_it_works_step4_title: "Вознаграждения",
      how_it_works_step4_body: "Поддерживающие получают особые амулеты и будущие токены в знак благодарности и причастности.",
    },
  },
};

export function getDictionary(locale: Locale = "he"): Dictionary {
  return dictionaries[locale] ?? dictionaries.he;
}
