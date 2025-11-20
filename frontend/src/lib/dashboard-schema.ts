import type { HeroSectionProps } from "@/components/blocks/hero-section";
import type { LiveConsoleProps } from "@/components/live-console";
import type { OperationsPanelProps } from "@/components/operations-panel";
import type { TonBalanceCardProps } from "@/components/ton-balance-card";

export type DashboardBlock =
  | ({ id: string; columnSpan?: number } & ({ type: "hero"; props: HeroSectionProps } | { type: "liveConsole"; props: LiveConsoleProps } | { type: "operations"; props: OperationsPanelProps } | { type: "tonBalance"; props: TonBalanceCardProps }));

export interface DashboardSection {
  id: string;
  layout: "full" | "grid";
  columns?: 2 | 3;
  blocks: DashboardBlock[];
}

export const dashboardSections: DashboardSection[] = [
  {
    id: "hero",
    layout: "full",
    blocks: [
      {
        id: "masthead",
        type: "hero",
        props: {
          eyebrow: "SOD Autonomous Corporation",
          title: "Command Center",
          description:
            "A hardened offline-ready interface to supervise and activate the Python backend. Monitor live logs and dispatch mission-critical directives with confidence.",
          ctaLabel: "Review Backend",
          ctaHref: "http://backend:8000/docs",
          secondaryCta: { label: "Learn More", href: "https://ton.org" },
        },
      },
    ],
  },
  {
    id: "operations",
    layout: "grid",
    columns: 3,
    blocks: [
      {
        id: "console",
        type: "liveConsole",
        columnSpan: 2,
        props: {
          title: "Live Console",
          description: "Streaming updates from http://backend:8000/logs",
          endpoint: "/logs",
          pollIntervalMs: 5000,
        },
      },
      {
        id: "operations-panel",
        type: "operations",
        props: {
          title: "Operations",
          description: "Issue directives to the backend orchestration service.",
          endpoint: "/start-meeting",
          actionLabel: "Convene Council",
        },
      },
      {
        id: "ton",
        type: "tonBalance",
        props: {
          label: "Treasury Balance",
          endpoint: "/ton/balance",
        },
      },
    ],
  },
];
