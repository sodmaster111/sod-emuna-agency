import { defaultLang, Lang } from "./config";
import he from "./dictionaries/he.json";
import ru from "./dictionaries/ru.json";
import en from "./dictionaries/en.json";

export type Dictionary = typeof he;

const dictionaries: Record<Lang, Dictionary> = {
  he,
  ru,
  en,
};

export async function getDictionary(lang: Lang): Promise<Dictionary> {
  return dictionaries[lang] ?? dictionaries[defaultLang];
}
