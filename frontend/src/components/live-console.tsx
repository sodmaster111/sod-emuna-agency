"use client";

import { useEffect, useRef, useState } from "react";
import { Loader2, Radio } from "lucide-react";

import api from "@/lib/api";

export type LogsPayload = string | string[] | { logs?: unknown } | undefined;

export interface LiveConsoleProps {
  endpoint?: string;
  pollIntervalMs?: number;
  title?: string;
  description?: string;
}

function normalizeLogs(payload: LogsPayload): string[] {
  if (!payload) return [];

  if (typeof payload === "string") {
    return payload.split(/\r?\n/).filter((line) => line.trim().length > 0);
  }

  if (Array.isArray(payload)) {
    return payload.map((entry) => (typeof entry === "string" ? entry : JSON.stringify(entry)));
  }

  if (typeof payload === "object" && "logs" in payload) {
    const { logs } = payload as { logs?: unknown };
    return normalizeLogs(Array.isArray(logs) || typeof logs === "string" ? logs : undefined);
  }

  return [];
}

export function LiveConsole({
  endpoint = "/logs",
  pollIntervalMs = 5000,
  title = "Live Console",
  description = "Streaming logs from the backend",
}: LiveConsoleProps) {
  const [logs, setLogs] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let isMounted = true;
    const fallbackMessage = "Data temporarily unavailable. Please try again later.";

    const fetchLogs = async () => {
      try {
        const response = await api.get<LogsPayload>(endpoint);
        if (!isMounted) return;

        setLogs(normalizeLogs(response.data));
        setError(null);
      } catch (err) {
        if (!isMounted) return;
        setError(fallbackMessage);
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, pollIntervalMs);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [endpoint, pollIntervalMs]);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <section className="space-y-4 rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-2xl shadow-emerald-500/10">
      <header className="flex items-center justify-between">
        <div className="flex items-center gap-3 text-slate-200">
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-300">
            <Radio className="h-5 w-5" />
          </span>
          <div>
            <p className="text-xs uppercase tracking-[0.25em] text-emerald-300">{title}</p>
            <p className="text-sm text-slate-400">{description}</p>
          </div>
        </div>
        {isLoading ? (
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Initializing feed…</span>
          </div>
        ) : null}
      </header>

      {error ? (
        <div className="rounded-xl border border-amber-400/40 bg-amber-500/10 p-4 text-sm text-amber-100">
          {error}
        </div>
      ) : null}

      <div
        ref={containerRef}
        className="h-[28rem] rounded-2xl border border-slate-800 bg-black/70 p-4 font-mono text-sm text-emerald-200 shadow-inner"
      >
        {error ? (
          <div className="flex h-full items-center justify-center text-center text-amber-200">{error}</div>
        ) : logs.length === 0 ? (
          <div className="flex h-full items-center justify-center text-slate-400">Awaiting backend output…</div>
        ) : (
          <div className="space-y-2">
            {logs.map((entry, index) => (
              <div key={`${entry}-${index}`} className="whitespace-pre-wrap leading-relaxed">
                {entry}
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
