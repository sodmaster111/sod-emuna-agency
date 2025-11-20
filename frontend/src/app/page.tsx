"use client";

import {
  Activity,
  Brain,
  Coins,
  Cpu,
  FileText,
  Radio,
  TrendingUp,
} from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import type { ComponentType } from "react";

import { DonationForm } from "@/components/blocks/donation-form";
import { HeroSection } from "@/components/blocks/hero-section";
import { LiveLog } from "@/components/blocks/live-log";
import { NftGrid } from "@/components/blocks/nft-grid";
import { StatsCard } from "@/components/blocks/stats-card";
import { API_BASE_URL, CMS_ROUTES } from "@/lib/config";

type HeroSectionConfig = {
  type: "hero";
  eyebrow?: string;
  title: string;
  description?: string;
  ctaLabel?: string;
  ctaHref?: string;
  secondaryCta?: {
    label: string;
    href: string;
  };
};

type StatsSectionConfig = {
  type: "stats";
  items: {
    label: string;
    value: string;
    description?: string;
    icon?: string;
    trend?: { direction: "up" | "down"; value: string };
  }[];
};

type LiveLogSectionConfig = {
  type: "live_log";
  title?: string;
  entries?: { id?: string | number; speaker?: string; message: string; timestamp?: string }[];
};

type NftGridSectionConfig = {
  type: "nft_grid";
  title?: string;
  subtitle?: string;
  items?: {
    id?: string | number;
    title: string;
    image?: string;
    description?: string;
    badge?: string;
  }[];
};

type DonationSectionConfig = {
  type: "donation_form";
  title?: string;
  description?: string;
  ctaLabel?: string;
};

type LayoutSection =
  | HeroSectionConfig
  | StatsSectionConfig
  | LiveLogSectionConfig
  | NftGridSectionConfig
  | DonationSectionConfig;

type LayoutResponse = {
  sections: LayoutSection[];
};

const iconMap: Record<string, ComponentType<any>> = {
  activity: Activity,
  brain: Brain,
  cpu: Cpu,
  radio: Radio,
  revenue: Coins,
  trending: TrendingUp,
  log: FileText,
};

async function fetchLayout(): Promise<LayoutResponse> {
  const response = await fetch(`${API_BASE_URL}${CMS_ROUTES.layout}`, { cache: "no-store" });

  if (!response.ok) {
    throw new Error("Failed to load layout");
  }

  return response.json();
}

export default function DynamicPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["layout"],
    queryFn: fetchLayout,
    staleTime: 10 * 1000,
  });

  return (
    <main className="mx-auto max-w-6xl space-y-8 px-6 py-10">
      {isLoading ? <SkeletonLayout /> : null}
      {error ? (
        <div className="rounded-2xl border border-red-500/40 bg-red-500/10 p-6 text-red-200">
          Unable to reach the AI layout orchestrator.
        </div>
      ) : null}
      {data?.sections?.map((section, index) => (
        <SectionRenderer key={(section as { id?: string })?.id ?? index} section={section} />
      ))}
    </main>
  );
}

function SectionRenderer({ section }: { section: LayoutSection }) {
  switch (section.type) {
    case "hero":
      return (
        <HeroSection
          eyebrow={section.eyebrow}
          title={section.title}
          description={section.description}
          ctaHref={section.ctaHref}
          ctaLabel={section.ctaLabel}
          secondaryCta={section.secondaryCta}
        />
      );
    case "stats":
      return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {section.items.map((item, index) => {
            const Icon = item.icon ? iconMap[item.icon] : undefined;
            return (
              <StatsCard
                key={`${item.label}-${index}`}
                label={item.label}
                value={item.value}
                description={item.description}
                icon={Icon}
                trend={item.trend}
              />
            );
          })}
        </div>
      );
    case "live_log":
      return <LiveLog title={section.title} entries={section.entries} />;
    case "nft_grid":
      return <NftGrid title={section.title} subtitle={section.subtitle} items={section.items} />;
    case "donation_form":
      return (
        <DonationForm title={section.title} description={section.description} ctaLabel={section.ctaLabel} />
      );
    default:
      return null;
  }
}

function SkeletonLayout() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-48 rounded-3xl bg-white/5" />
      <div className="grid gap-4 md:grid-cols-3">
        {[1, 2, 3].map((item) => (
          <div key={item} className="h-28 rounded-2xl bg-white/5" />
        ))}
      </div>
      <div className="h-80 rounded-2xl bg-white/5" />
    </div>
  );
}
