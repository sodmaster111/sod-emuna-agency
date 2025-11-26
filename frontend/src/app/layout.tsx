import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "SOD Emuna Agency",
    template: "%s | SOD Emuna Agency",
  },
  description: "Autonomous AI-driven agency for spreading emuna and Torah (SOD).",
  openGraph: {
    title: "SOD Emuna Agency",
    description: "Autonomous AI-driven agency for spreading emuna and Torah.",
    url: "https://sodmaster.online",
    siteName: "SOD Emuna Agency",
    locale: "he-IL",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "SOD Emuna Agency",
    description: "Autonomous AI-driven agency for spreading emuna and Torah.",
  },
  alternates: {
    languages: {
      he: "https://sodmaster.online/?lang=he",
      ru: "https://sodmaster.online/?lang=ru",
      en: "https://sodmaster.online/?lang=en",
    },
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-50 antialiased">{children}</body>
    </html>
  );
}
