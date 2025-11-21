import type { ChannelCount, DailyCount } from "@/app/lib/metrics";
import SimpleChart from "./simple-chart";

type AnalyticsOverviewProps = {
  pinkasPerDay: DailyCount[];
  missionsPerDay: DailyCount[];
  messagesPerChannel: ChannelCount[];
};

function totalCount(items: { count: number }[]): number {
  return items.reduce((sum, item) => sum + item.count, 0);
}

function formatDailyData(items: DailyCount[]): { label: string; value: number }[] {
  return items.map((item) => ({ label: item.date, value: item.count }));
}

function formatChannelData(items: ChannelCount[]): { label: string; value: number }[] {
  return items.map((item) => ({ label: item.channel, value: item.count }));
}

export default function AnalyticsOverview({
  pinkasPerDay,
  missionsPerDay,
  messagesPerChannel,
}: AnalyticsOverviewProps) {
  const summaryCards = [
    {
      title: "Pinkas entries (last 7 days)",
      value: totalCount(pinkasPerDay),
      description: "Captured from operations log",
    },
    {
      title: "Missions executed (last 7 days)",
      value: totalCount(missionsPerDay),
      description: "Scheduled and completed runs",
    },
    {
      title: "Messages sent (by channel)",
      value: totalCount(messagesPerChannel),
      description: "Telegram & WhatsApp volume",
    },
  ];

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">
        {summaryCards.map((card) => (
          <div
            key={card.title}
            className="rounded-xl border border-white/10 bg-slate-800/60 p-5 shadow-sm shadow-black/30"
          >
            <p className="text-xs uppercase tracking-wide text-slate-400">{card.title}</p>
            <p className="mt-2 text-3xl font-semibold text-white">{card.value}</p>
            <p className="mt-1 text-sm text-slate-300">{card.description}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="rounded-xl border border-white/10 bg-slate-900/50 p-6 lg:col-span-2">
          <SimpleChart title="Pinkas entries per day" data={formatDailyData(pinkasPerDay)} />
        </div>
        <div className="rounded-xl border border-white/10 bg-slate-900/50 p-6">
          <SimpleChart title="Missions executed per day" data={formatDailyData(missionsPerDay)} />
        </div>
      </div>

      <div className="rounded-xl border border-white/10 bg-slate-900/50 p-6">
        <SimpleChart title="Messages sent by channel" data={formatChannelData(messagesPerChannel)} />
      </div>
    </div>
  );
}
