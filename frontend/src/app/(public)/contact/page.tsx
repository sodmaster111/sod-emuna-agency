import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Contact",
  description: "Get in touch with SOD Emuna Agency.",
};

export default function ContactPage() {
  return (
    <main className="min-h-screen">
      <section className="mx-auto max-w-4xl space-y-6 px-6 py-12">
        <p className="text-sm uppercase tracking-[0.35em] text-emerald-300">Contact</p>
        <div className="space-y-3">
          <h1 className="text-4xl font-bold sm:text-5xl">Get in Touch</h1>
          <p className="text-lg text-slate-300">
            Reach out to the SOD Emuna Agency team for collaborations, support, or to share feedback on our mission-driven
            work.
          </p>
        </div>
        <div className="space-y-4 rounded-3xl border border-slate-800 bg-slate-900/70 p-8 shadow-2xl shadow-emerald-500/10">
          <p className="text-slate-200">Email: contact@sodmaster.online</p>
          <p className="text-slate-200">Telegram: @sodmaster</p>
          <p className="text-slate-200">Community updates: subscribe for launch notices and project news.</p>
        </div>
      </section>
    </main>
  );
}
