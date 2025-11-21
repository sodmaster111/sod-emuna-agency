import AnalyticsOverview from "@/app/components/dashboard/analytics-overview";
import { getAnalyticsSummary } from "@/app/lib/metrics";

export default async function AnalyticsDashboardPage() {
  let error: string | null = null;
  let summary: Awaited<ReturnType<typeof getAnalyticsSummary>> | null = null;

  try {
    summary = await getAnalyticsSummary();
  } catch (err) {
    error = err instanceof Error ? err.message : "Failed to load analytics";
  }

  if (error) {
    return (
      <div className="space-y-3 rounded-xl border border-rose-400/40 bg-rose-950/40 p-6 text-rose-100">
        <p className="font-semibold">Analytics unavailable</p>
        <p className="text-sm text-rose-200/80">{error}</p>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="rounded-xl border border-white/10 bg-slate-900/50 p-6 text-slate-200">
        Loading analytics...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h2 className="text-2xl font-semibold text-white">Analytics</h2>
        <p className="text-sm text-slate-300">
          Track activity across Pinkas logging, mission runs, and outbound messaging. These metrics are fetched
          from the backend analytics summary endpoint.
        </p>
      </div>

      <AnalyticsOverview
        pinkasPerDay={summary.pinkas_per_day}
        missionsPerDay={summary.missions_per_day}
        messagesPerChannel={summary.messages_sent_per_channel}
      />
    </div>
  );
}
