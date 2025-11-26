export type Locale = "he" | "en" | "ru";

export type PublicDictionary = {
  donate: {
    title: string;
    subtitle: string;
    amount_label: string;
    contact_title: string;
    submit_success: string;
  };
};

const dictionaries: Record<Locale, PublicDictionary> = {
  he: {
    donate: {
      title: "תרומה לקהילת SOD",
      subtitle: "כל תרומה מחזקת את היכולת שלנו לפתח כלים פיננסיים ואוטומציה עבור הציבור.",
      amount_label: "סכום התרומה (TON)",
      contact_title: "פרטי קשר",
      submit_success: "תודה! קיבלנו את בקשת התרומה שלך ונחזור אליך לאישור.",
    },
  },
  en: {
    donate: {
      title: "Support the SOD mission",
      subtitle: "Your contribution fuels open finance experiments and community infrastructure.",
      amount_label: "Donation amount (TON)",
      contact_title: "Contact details",
      submit_success: "Thank you! We logged your pledge and will confirm the transfer shortly.",
    },
  },
  ru: {
    donate: {
      title: "Поддержать проект SOD",
      subtitle: "Ваш вклад ускоряет наши финансовые сервисы и инструменты автоматизации для сообщества.",
      amount_label: "Сумма пожертвования (TON)",
      contact_title: "Контактные данные",
      submit_success: "Спасибо! Мы получили заявку на пожертвование и подтвердим перевод в ближайшее время.",
    },
  },
};

export function getDictionary(lang?: string): PublicDictionary {
  const normalized = (lang ?? "he").toLowerCase() as Locale;
  return dictionaries[normalized] ?? dictionaries.he;
}
