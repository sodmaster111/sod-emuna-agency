import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Mission",
  description: "Our mission: daily tefillah, Torah spreading, community.",
};

export default function MissionPage() {
  return (
    <main className="min-h-screen">
      <section className="mx-auto max-w-4xl space-y-6 px-6 py-12">
        <p className="text-sm uppercase tracking-[0.35em] text-emerald-300">Mission</p>
        <div className="space-y-3">
          <h1 className="text-4xl font-bold sm:text-5xl">Purpose &amp; Practice</h1>
          <p className="text-lg text-slate-300">
            We aim to elevate daily tefillah, spread Torah learning, and build a resilient global community through
            autonomous, transparent systems.
          </p>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {[
            {
              title: "Daily Tefillah",
              body: "Automating reminders and shared kavanos to unite people in consistent prayer.",
            },
            {
              title: "Torah Spreading",
              body: "Delivering Torah insights across channels with fidelity and care for the source.",
            },
            {
              title: "Community",
              body: "Building tools that strengthen connection and mutual support wherever members are located.",
            },
          ].map((item) => (
            <div
              key={item.title}
              className="space-y-2 rounded-2xl border border-slate-800 bg-slate-900/70 p-6 shadow-lg shadow-emerald-500/10"
            >
              <h2 className="text-xl font-semibold text-slate-100">{item.title}</h2>
              <p className="text-slate-300">{item.body}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
