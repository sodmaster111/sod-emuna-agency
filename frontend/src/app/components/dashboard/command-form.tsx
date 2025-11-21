"use client";

import { useState } from "react";
import { getCommandStatus, scheduleCommand, type CommandStatusResponse } from "@/app/lib/api";
import { Button } from "@/app/ui/button";

const agents = [
  "orchestrator",
  "scout",
  "nasi",
  "levi",
  "zevulun",
  "issachar",
  "asher",
  "dan",
  "naphtali",
  "gad",
  "reuben",
  "simeon",
];

export default function CommandForm() {
  const [agentName, setAgentName] = useState(agents[0]);
  const [payload, setPayload] = useState("{\n  \"task\": \"ping\"\n}");
  const [taskId, setTaskId] = useState<string | null>(null);
  const [statusResult, setStatusResult] = useState<CommandStatusResponse | null>(null);
  const [statusLookupId, setStatusLookupId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSchedule(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setStatusResult(null);
    setLoading(true);

    try {
      const parsedPayload = JSON.parse(payload);
      const response = await scheduleCommand({ agent_name: agentName, payload: parsedPayload });
      setTaskId(response.task_id);
      setStatusLookupId(response.task_id);
    } catch (err) {
      const message =
        err instanceof SyntaxError
          ? "Payload must be valid JSON"
          : err instanceof Error
            ? err.message
            : "Unable to schedule command";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  async function handleStatusCheck() {
    if (!statusLookupId) {
      setError("Provide a task_id to check status");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const status = await getCommandStatus(statusLookupId);
      setStatusResult(status);
    } catch (err) {
      setStatusResult(null);
      setError(err instanceof Error ? err.message : "Unable to fetch status");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <form onSubmit={handleSchedule} className="space-y-4">
        <div className="space-y-1">
          <h3 className="text-lg font-semibold text-white">Schedule a mission</h3>
          <p className="text-sm text-slate-300">Select the target agent and provide a JSON payload.</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <label className="flex flex-col gap-2 text-sm text-slate-200">
            Agent name
            <select
              value={agentName}
              onChange={(e) => setAgentName(e.target.value)}
              className="rounded-lg border border-white/10 bg-slate-800 px-3 py-2 text-white focus:border-[var(--color-accent)] focus:outline-none"
            >
              {agents.map((agent) => (
                <option key={agent} value={agent}>
                  {agent}
                </option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-2 text-sm text-slate-200">
            Payload (JSON)
            <textarea
              value={payload}
              onChange={(e) => setPayload(e.target.value)}
              rows={6}
              className="h-full rounded-lg border border-white/10 bg-slate-800 px-3 py-2 font-mono text-sm text-white focus:border-[var(--color-accent)] focus:outline-none"
            />
          </label>
        </div>

        <Button type="submit" disabled={loading}>
          {loading ? "Scheduling..." : "Schedule command"}
        </Button>
      </form>

      <div className="space-y-3 rounded-xl border border-white/10 bg-slate-800/30 p-4">
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <label className="flex flex-1 flex-col gap-2 text-sm text-slate-200">
            task_id
            <input
              value={statusLookupId}
              onChange={(e) => setStatusLookupId(e.target.value)}
              placeholder="Paste task identifier"
              className="rounded-lg border border-white/10 bg-slate-900 px-3 py-2 text-white placeholder:text-slate-500 focus:border-[var(--color-accent)] focus:outline-none"
            />
          </label>
          <div className="flex justify-end pt-2 md:pt-0">
            <Button type="button" variant="secondary" onClick={handleStatusCheck} disabled={loading}>
              Check Status
            </Button>
          </div>
        </div>

        {taskId && (
          <p className="text-xs text-slate-400">
            Last scheduled task: <span className="text-white">{taskId}</span>
          </p>
        )}

        {statusResult && (
          <div className="space-y-1 rounded-lg border border-white/10 bg-slate-900/60 p-3 text-sm text-slate-100">
            <p className="flex justify-between text-xs uppercase tracking-wide text-slate-400">
              <span>Task</span>
              <span>{statusResult.task_id}</span>
            </p>
            <p>
              State: <span className="font-semibold text-white">{statusResult.state}</span>
            </p>
            {statusResult.summary && <p>Summary: {statusResult.summary}</p>}
            {statusResult.detail && <p>Detail: {statusResult.detail}</p>}
          </div>
        )}

        {error && (
          <div className="rounded-lg border border-rose-400/40 bg-rose-950/40 p-3 text-sm text-rose-100">
            {error}
          </div>
        )}
      </div>
    </div>
  );
}
