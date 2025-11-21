"use client";

// Client component to enable interactive filtering without full page reloads.
import { useEffect, useState } from "react";
import { getPinkas, type PinkasEntry } from "@/app/lib/api";
import PinkasTable from "@/app/components/dashboard/pinkas-table";
import { Button } from "@/app/ui/button";

const statusOptions = [
  { label: "Any", value: "" },
  { label: "Success", value: "success" },
  { label: "Failed", value: "failed" },
  { label: "Pending", value: "pending" },
];

const limitOptions = [20, 50, 100];

export default function PinkasPage() {
  const [agent, setAgent] = useState("");
  const [status, setStatus] = useState("");
  const [limit, setLimit] = useState(20);
  const [entries, setEntries] = useState<PinkasEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    async function loadPinkas() {
      setLoading(true);
      setError(null);
      try {
        const data = await getPinkas({
          agent: agent || undefined,
          status: status || undefined,
          limit,
        });
        if (isMounted) {
          setEntries(data.items);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Failed to load Pinkas entries");
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadPinkas();
    return () => {
      isMounted = false;
    };
  }, [agent, status, limit]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div className="space-y-1">
          <h2 className="text-2xl font-semibold text-white">Pinkas Logs</h2>
          <p className="text-sm text-slate-300">Filter, inspect, and drill into agent activity.</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <div className="flex flex-col text-sm">
            <label className="text-slate-400" htmlFor="agent">
              Agent
            </label>
            <input
              id="agent"
              value={agent}
              onChange={(e) => setAgent(e.target.value)}
              placeholder="agent name"
              className="rounded-lg border border-white/10 bg-slate-800 px-3 py-2 text-white placeholder:text-slate-500 focus:border-[var(--color-accent)] focus:outline-none"
            />
          </div>
          <div className="flex flex-col text-sm">
            <label className="text-slate-400" htmlFor="status">
              Status
            </label>
            <select
              id="status"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="rounded-lg border border-white/10 bg-slate-800 px-3 py-2 text-white focus:border-[var(--color-accent)] focus:outline-none"
            >
              {statusOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-col text-sm">
            <label className="text-slate-400" htmlFor="limit">
              Limit
            </label>
            <select
              id="limit"
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
              className="rounded-lg border border-white/10 bg-slate-800 px-3 py-2 text-white focus:border-[var(--color-accent)] focus:outline-none"
            >
              {limitOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <Button
              variant="secondary"
              onClick={() => {
                setAgent("");
                setStatus("");
                setLimit(20);
              }}
            >
              Reset
            </Button>
          </div>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-400/40 bg-rose-950/40 p-4 text-sm text-rose-100">
          {error}
        </div>
      )}

      <PinkasTable
        entries={entries}
        loading={loading}
        onRowClick={(id) => window.open(`/dashboard/pinkas/${id}`, "_self")}
      />
    </div>
  );
}
