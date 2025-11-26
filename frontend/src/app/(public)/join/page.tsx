import JoinCards from "@/app/components/public/JoinCards";
import PublicHeader from "@/app/components/public/PublicHeader";

const dict = {
  join: {
    title: "Join the community",
    intro:
      "Stay close to product updates, operator calls, and early experiments across the SOD ecosystem.",
    telegram_title: "Telegram collective",
    telegram_description: "Daily chatter, release drops, and quick polls with the core contributors.",
    whatsapp_title: "WhatsApp task force",
    whatsapp_description: "Mobile-first alerts when we spin up missions, AMAs, or coordination calls.",
    email_title: "Email newsletter",
    email_description: "Monthly digest for investors and operators who want a calm channel.",
    rules_title: "Community basics",
    rules: [
      "Stay on-topic and protect confidential or sensitive details.",
      "Be respectful—no spam, pump-and-dumps, or personal attacks.",
      "Use English for now; we will expand locales as the network scales.",
    ],
  },
};

export default function JoinPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      <PublicHeader />

      <main className="py-12 md:py-16">
        <div className="mx-auto max-w-6xl space-y-10 px-6">
          <section className="space-y-4">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold uppercase tracking-[0.25em] text-emerald-200">
              Join
              <span className="h-2 w-2 rounded-full bg-emerald-400" />
            </div>
            <h1 className="text-4xl font-bold leading-tight sm:text-5xl">{dict.join.title}</h1>
            <p className="max-w-3xl text-lg text-slate-300">{dict.join.intro}</p>
          </section>

          <section className="space-y-6">
            <JoinCards dict={dict} />

            <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-6 shadow-xl shadow-black/20">
              <div className="flex items-center gap-3">
                <span className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-300">
                  •
                </span>
                <div>
                  <p className="text-xs uppercase tracking-[0.25em] text-emerald-200">Guidelines</p>
                  <h2 className="text-xl font-semibold text-white">{dict.join.rules_title}</h2>
                </div>
              </div>

              <ul className="mt-4 space-y-3 text-sm leading-relaxed text-slate-300">
                {dict.join.rules.map((rule) => (
                  <li key={rule} className="flex items-start gap-3">
                    <span className="mt-1 inline-flex h-2 w-2 rounded-full bg-emerald-400" />
                    <span>{rule}</span>
                  </li>
                ))}
              </ul>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
