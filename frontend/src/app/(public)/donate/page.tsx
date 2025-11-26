import { DonationForm } from "@/app/components/donate/DonationForm";
import { DonationSummary } from "@/app/components/donate/DonationSummary";

import { Container } from "../components/Container";
import { Section } from "../components/Section";
import { getDictionary } from "../i18n/dictionaries";

interface DonatePageProps {
  searchParams?: {
    lang?: string;
  };
}

export default function DonatePage({ searchParams }: DonatePageProps) {
  const dict = getDictionary(searchParams?.lang);

  return (
    <Container>
      <Section className="space-y-10">
        <div className="space-y-6 text-center">
          <h1 className="text-4xl font-bold text-[var(--color-text)] sm:text-5xl">{dict.donate.title}</h1>
          <DonationSummary copy={dict.donate} />
        </div>

        <div className="mx-auto max-w-3xl">
          <DonationForm copy={dict.donate} />
        </div>
      </Section>
    </Container>
  );
}
