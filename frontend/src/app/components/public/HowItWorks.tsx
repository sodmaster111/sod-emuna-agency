import type { HomeDictionary } from "@/app/dictionaries";
import { Container, Section } from "./layout";

type HowItWorksProps = {
  content: HomeDictionary;
};

const stepsOrder = [
  "how_it_works_step1",
  "how_it_works_step2",
  "how_it_works_step3",
  "how_it_works_step4",
] as const;

type StepKey = (typeof stepsOrder)[number];

function resolveStepContent(content: HomeDictionary, baseKey: StepKey) {
  const label = baseKey.replace("how_it_works_", "").toUpperCase();
  return {
    title: content[`${baseKey}_title` as keyof HomeDictionary],
    body: content[`${baseKey}_body` as keyof HomeDictionary],
    label,
  } as const;
}

export function HowItWorks({ content }: HowItWorksProps) {
  const steps = stepsOrder.map((key) => resolveStepContent(content, key));

  return (
    <Section className="bg-slate-900/30" id="how-it-works">
      <Container className="space-y-10">
        <div className="space-y-3 text-center">
          <p className="text-sm uppercase tracking-[0.3em] text-emerald-300">SOD</p>
          <h2 className="text-3xl font-semibold text-white sm:text-4xl">{content.how_it_works_title}</h2>
          <p className="mx-auto max-w-2xl text-base text-slate-300">
            פשטות שמדגישה את השילוב בין סוכני AMAC, ערוצי הקהילה, והאוצר בטון שמזרים משימות ותגמולים.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
          {steps.map((step, index) => (
            <article
              key={step.label}
              className="flex h-full flex-col gap-4 rounded-2xl border border-white/10 bg-slate-950/40 p-6 shadow-lg shadow-black/20"
            >
              <div className="flex items-center justify-between text-sm font-semibold text-emerald-200">
                <span className="flex h-9 w-9 items-center justify-center rounded-full bg-emerald-500/10 text-base text-emerald-300">
                  {index + 1}
                </span>
                <span className="text-xs uppercase tracking-[0.2em] text-slate-400">{step.label}</span>
              </div>
              <div className="space-y-2">
                <h3 className="text-lg font-semibold text-white">{step.title}</h3>
                <p className="text-sm leading-relaxed text-slate-200">{step.body}</p>
              </div>
            </article>
          ))}
        </div>
      </Container>
    </Section>
  );
}
