import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sod Emuna Agency",
  description: "Operational intelligence and coordination for the autonomous council.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
