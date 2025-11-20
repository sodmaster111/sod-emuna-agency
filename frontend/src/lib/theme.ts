import { API_BASE_URL, CMS_ROUTES } from "./config";

export type ThemePalette = {
  name?: string;
  mode?: "light" | "dark" | string;
  background?: string;
  surface?: string;
  card?: string;
  primary?: string;
  accent?: string;
  text?: string;
  muted?: string;
  border?: string;
};

export const DEFAULT_THEME: ThemePalette = {
  name: "Midnight",
  mode: "dark",
  background: "#020617",
  surface: "#0b1224",
  card: "#0f172a",
  primary: "#22c55e",
  accent: "#38bdf8",
  text: "#e2e8f0",
  muted: "#94a3b8",
  border: "#1e293b",
};

export async function fetchThemePalette(): Promise<ThemePalette> {
  const response = await fetch(`${API_BASE_URL}${CMS_ROUTES.theme}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to load theme from CMS");
  }

  const data = (await response.json()) as ThemePalette;
  return { ...DEFAULT_THEME, ...data };
}

export function applyThemeVariables(palette: ThemePalette) {
  if (typeof document === "undefined") return;

  const root = document.documentElement;
  const theme = { ...DEFAULT_THEME, ...palette };

  const variables: Record<string, string> = {
    "--color-bg": theme.background ?? DEFAULT_THEME.background!,
    "--color-surface": theme.surface ?? DEFAULT_THEME.surface!,
    "--color-card": theme.card ?? DEFAULT_THEME.card!,
    "--color-primary": theme.primary ?? DEFAULT_THEME.primary!,
    "--color-accent": theme.accent ?? DEFAULT_THEME.accent!,
    "--color-text": theme.text ?? DEFAULT_THEME.text!,
    "--color-muted": theme.muted ?? DEFAULT_THEME.muted!,
    "--color-border": theme.border ?? DEFAULT_THEME.border!,
  };

  Object.entries(variables).forEach(([key, value]) => {
    root.style.setProperty(key, value);
  });

  if (theme.mode) {
    root.style.setProperty("color-scheme", theme.mode);
  }
}
