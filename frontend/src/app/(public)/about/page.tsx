import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "About SOD",
  description: "Background, story and vision of SOD Emuna Agency.",
};

export default function AboutPage() {
  return (
    <main className="min-h-screen">
      <section className="mx-auto max-w-4xl space-y-6 px-6 py-12">
        <p className="text-sm uppercase tracking-[0.35em] text-emerald-300">SOD Emuna Agency</p>
        <div className="space-y-3">
          <h1 className="text-4xl font-bold sm:text-5xl">About the Agency</h1>
          <p className="text-lg text-slate-300">
            Explore the background, story, and guiding vision behind the SOD Emuna Agency. Discover how we blend
            autonomous systems with Torah values to strengthen emuna and uplift communities.
          </p>
        </div>
        <div className="space-y-4 rounded-3xl border border-slate-800 bg-slate-900/70 p-8 shadow-2xl shadow-emerald-500/10">
          <p className="text-slate-200">
            Our team combines engineering rigor with spiritual mission. Each initiative is built to be resilient,
            transparent, and aligned with the community&apos;s needs, ensuring technology serves as a bridge to deeper
            connection.
          </p>
        </div>
      </section>
    </main>
  );
}
