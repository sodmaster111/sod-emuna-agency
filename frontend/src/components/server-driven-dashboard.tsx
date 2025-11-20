import type { ElementType } from "react";

import { HeroSection } from "@/components/blocks/hero-section";
import { LiveConsole } from "@/components/live-console";
import { OperationsPanel } from "@/components/operations-panel";
import { TonBalanceCard } from "@/components/ton-balance-card";
import type { DashboardBlock, DashboardSection } from "@/lib/dashboard-schema";

interface ServerDrivenDashboardProps {
  sections: DashboardSection[];
}

const COMPONENT_REGISTRY: Record<DashboardBlock["type"], ElementType> = {
  hero: HeroSection,
  liveConsole: LiveConsole,
  operations: OperationsPanel,
  tonBalance: TonBalanceCard,
};

function RenderBlock({ block }: { block: DashboardBlock }) {
  const Component = COMPONENT_REGISTRY[block.type];
  if (!Component) return null;

  return <Component {...block.props} />;
}

export function ServerDrivenDashboard({ sections }: ServerDrivenDashboardProps) {
  return (
    <div className="mx-auto max-w-6xl space-y-8 px-6 py-12">
      {sections.map((section) => {
        const columnsClass = section.columns === 2 ? "lg:grid-cols-2" : "lg:grid-cols-3";

        if (section.layout === "grid") {
          return (
            <div key={section.id} className={`grid gap-6 ${columnsClass}`}>
              {section.blocks.map((block) => (
                <div
                  key={block.id}
                  className={block.columnSpan === 2 ? "lg:col-span-2" : block.columnSpan === 3 ? "lg:col-span-3" : ""}
                >
                  <RenderBlock block={block} />
                </div>
              ))}
            </div>
          );
        }

        return (
          <div key={section.id} className="space-y-6">
            {section.blocks.map((block) => (
              <RenderBlock key={block.id} block={block} />
            ))}
          </div>
        );
      })}
    </div>
  );
}
