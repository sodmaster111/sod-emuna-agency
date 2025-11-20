import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SOD Autonomous Corporation | Command Center",
  description: "Offline-ready dashboard to direct the SOD Python backend.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-50 antialiased" style={{ fontFamily: "sans-serif" }}>
        {children}
      </body>
    </html>
  );
}
