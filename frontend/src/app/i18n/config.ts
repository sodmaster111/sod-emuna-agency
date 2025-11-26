export const languages = ["he", "ru", "en"] as const;
export type Lang = (typeof languages)[number];
export const defaultLang: Lang = "he";
