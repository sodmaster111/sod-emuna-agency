import { getHealth } from "@/app/lib/api";

export default async function DashboardOverviewPage() {
  let healthStatus: Awaited<ReturnType<typeof getHealth>> | null = null;
  let errorMessage: string | null = null;

  try {
    healthStatus = await getHealth();
  } catch (error) {
    errorMessage = error instanceof Error ? error.message : "Unable to load health status";
  }

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h2 className="text-2xl font-semibold text-white">Overview</h2>
        <p className="text-sm text-slate-300">
          Monitor backend readiness, review Pinkas logs, and orchestrate manual missions for the
          agency. This Command Center is intended for the Nasi / management team.
        </p>
      </div>

      {healthStatus ? (
        <div className="grid gap-4 rounded-xl border border-white/10 bg-slate-800/50 p-6 md:grid-cols-3">
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-400">Overall</p>
            <p className="text-lg font-semibold text-white">{healthStatus.status}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-400">Database</p>
            <p className="text-lg font-semibold text-white">
              {healthStatus.services?.database ?? "unknown"}
            </p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-400">Celery</p>
            <p className="text-lg font-semibold text-white">
              {healthStatus.services?.celery ?? "unknown"}
            </p>
          </div>
        </div>
      ) : (
        <div className="rounded-xl border border-rose-400/40 bg-rose-950/40 p-6 text-rose-100">
          <p className="font-semibold">Health check failed</p>
          <p className="text-sm text-rose-200/80">{errorMessage}</p>
        </div>
      )}

      <div className="space-y-3 rounded-xl border border-white/10 bg-slate-800/30 p-6">
        <h3 className="text-lg font-semibold text-white">What you can do here</h3>
        <ul className="list-disc space-y-1 pl-5 text-sm text-slate-200">
          <li>Check real-time backend health signals.</li>
          <li>Inspect Pinkas logs with filters for agents and statuses.</li>
          <li>Schedule manual missions and track their execution.</li>
        </ul>
      </div>
    </div>
  );
}
