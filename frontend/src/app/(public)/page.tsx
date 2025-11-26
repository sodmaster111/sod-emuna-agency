import { ArrowRight, Radio, ShieldCheck, Sparkles } from "lucide-react";

import { Badge } from "@/app/components/ui/Badge";
import { Container } from "@/app/components/ui/Container";
import { Section } from "@/app/components/ui/Section";
import { Button } from "@/app/ui/button";

const features = [
  {
    title: "Operational visibility",
    description: "Live signals from every node in the council so you can brief leadership with confidence.",
    icon: Radio,
  },
  {
    title: "Decision support",
    description: "Structured briefs, Pinkas logs, and curated intelligence for the Nasi and Gabayim.",
    icon: ShieldCheck,
  },
  {
    title: "Human + machine",
    description: "Blend autonomous agents with human oversight to keep missions aligned with the halachic guardrails.",
    icon: Sparkles,
  },
];

const highlights = [
  {
    label: "שבת",
    value: "Shabbat-ready failsafes across the network.",
  },
  {
    label: "חדש",
    value: "Fresh mission templates for crisis response and coordination.",
  },
  {
    label: "Soon",
    value: "Dark mode palette to mirror the ops dashboard.",
  },
];

export default function PublicHomePage() {
  return (
    <main className="min-h-screen bg-sod-bg text-sod-text">
      <Section className="bg-white/60 pb-16 pt-20">
        <Container className="grid items-center gap-12 lg:grid-cols-[1.15fr_1fr]">
          <div className="space-y-6">
            <Badge variant="default">Sod Emuna Agency</Badge>
            <div className="space-y-3">
              <h1 className="text-4xl font-semibold leading-tight sm:text-5xl">
                A unified presence for the autonomous council
              </h1>
              <p className="max-w-2xl text-lg leading-relaxed text-slate-700">
                Operate with clarity. Coordinate the Sanhedrin, keep stakeholders informed, and deliver reliable updates for
                every mission cycle.
              </p>
            </div>

            <div className="flex flex-wrap gap-4">
              <Button className="bg-sod-primary text-white shadow-lg shadow-sod-primary/20 hover:-translate-y-0.5 hover:shadow-xl">
                Begin a mission
                <ArrowRight className="h-4 w-4" />
              </Button>
              <Button
                variant="secondary"
                className="border-sod-primary text-sod-primary hover:border-sod-accent hover:text-sod-text"
                asChild
                href="/login"
              >
                <a className="inline-flex items-center gap-2">Enter dashboard</a>
              </Button>
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              {highlights.map((item) => (
                <div
                  key={item.label}
                  className="rounded-2xl border border-slate-200 bg-white/80 p-4 shadow-sm shadow-slate-100"
                >
                  <Badge className="mb-3 text-xs" variant="outline">
                    {item.label}
                  </Badge>
                  <p className="text-sm text-slate-700">{item.value}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-xl shadow-sod-primary/10">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-sod-primary">Command status</p>
                <p className="text-lg font-semibold text-sod-text">Mission control is online</p>
              </div>
              <span className="inline-flex items-center gap-2 rounded-full bg-sod-primarySoft px-3 py-1 text-xs font-semibold text-sod-primary">
                <span className="h-2 w-2 rounded-full bg-sod-primary" />
                Live
              </span>
            </div>
            <div className="mt-6 space-y-3 text-sm text-slate-700">
              <p>
                Real-time telemetry feeds update every few seconds, ready to funnel into the operations dashboard for deeper
                action.
              </p>
              <p>
                Use the dashboard to dispatch directives, watch Pinkas updates, and ensure every agent stays aligned with the
                mission brief.
              </p>
            </div>
            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              <div className="rounded-2xl bg-sod-primarySoft p-4 text-sod-primary">
                <p className="text-xs uppercase tracking-wide">Uptime</p>
                <p className="text-2xl font-semibold">99.9%</p>
                <p className="text-xs text-sod-text/70">Automated health probes</p>
              </div>
              <div className="rounded-2xl border border-slate-200 p-4 text-sod-text">
                <p className="text-xs uppercase tracking-wide">Pinkas</p>
                <p className="text-2xl font-semibold">Live feed</p>
                <p className="text-xs text-sod-text/70">Streaming status lines</p>
              </div>
            </div>
          </div>
        </Container>
      </Section>

      <Section>
        <Container className="space-y-8">
          <div className="space-y-3 text-center">
            <Badge variant="outline" className="mx-auto w-fit">Agency Highlights</Badge>
            <h2 className="text-3xl font-semibold sm:text-4xl">Built for clarity and trust</h2>
            <p className="text-base text-slate-700 sm:text-lg">
              Bring the same discipline from the operations dashboard to the public-facing briefings and updates.
            </p>
          </div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="flex flex-col gap-3 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
              >
                <span className="inline-flex h-11 w-11 items-center justify-center rounded-xl bg-sod-primarySoft text-sod-primary">
                  <feature.icon className="h-5 w-5" />
                </span>
                <h3 className="text-xl font-semibold">{feature.title}</h3>
                <p className="text-sm leading-relaxed text-slate-700">{feature.description}</p>
              </div>
            ))}
          </div>
        </Container>
      </Section>
    </main>
  );
}
