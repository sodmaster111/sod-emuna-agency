import CommandInput from "@/components/command-input";
import Header from "@/components/header";
import KpiCard from "@/components/kpi-card";
import MeetingLog from "@/components/meeting-log";

export default function DashboardPage() {
  return (
    <main className="mx-auto max-w-6xl space-y-6 p-6">
      <Header />
      <section className="grid gap-4 md:grid-cols-3">
        <KpiCard label="Wealth Target" value="$1,000,000" subtext="North Star metric" />
        <KpiCard label="Current Cycle" value="Board in session" subtext="AutoGen orchestrator live" />
        <KpiCard label="API" value="FastAPI :8000" subtext="Connected" />
      </section>
      <section className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <MeetingLog />
        </div>
        <div className="lg:col-span-1">
          <CommandInput />
        </div>
      </section>
    </main>
  );
}
