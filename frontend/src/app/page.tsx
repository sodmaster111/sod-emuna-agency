"use client";

import { useEffect, useRef, useState } from "react";
import { Loader2, Play, Radio } from "lucide-react";

import api from "@/lib/api";

const POLL_INTERVAL_MS = 5000;

type CommandState = "idle" | "running" | "success" | "error";

type LogsPayload = string | string[] | { logs?: unknown } | undefined;

function normalizeLogs(payload: LogsPayload): string[] {
  if (!payload) return [];

  if (typeof payload === "string") {
    return payload.split(/\r?\n/).filter((line) => line.trim().length > 0);
  }

  if (Array.isArray(payload)) {
    return payload.map((entry) => (typeof entry === "string" ? entry : JSON.stringify(entry)));
  }

  if (typeof payload === "object" && payload !== null && "logs" in payload) {
    const { logs } = payload as { logs?: unknown };
    return normalizeLogs(Array.isArray(logs) || typeof logs === "string" ? logs : undefined);
  }

  return [];
}

export default function CommandCenterPage() {
  const [logs, setLogs] = useState<string[]>([]);
  const [isLoadingLogs, setIsLoadingLogs] = useState(true);
  const [logError, setLogError] = useState<string | null>(null);
  const [commandState, setCommandState] = useState<CommandState>("idle");
  const [commandMessage, setCommandMessage] = useState<string | null>(null);
  const consoleRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let isMounted = true;

    const fetchLogs = async () => {
      try {
        const response = await api.get<LogsPayload>("/logs");
        if (!isMounted) return;
        setLogs(normalizeLogs(response.data));
        setLogError(null);
      } catch (error) {
        if (!isMounted) return;
        setLogError("Unable to reach backend logs. The system will retry automatically.");
      } finally {
        if (isMounted) {
          setIsLoadingLogs(false);
        }
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, POLL_INTERVAL_MS);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    if (consoleRef.current) {
      consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
    }
  }, [logs]);

  const handleStartMeeting = async () => {
    setCommandState("running");
    setCommandMessage(null);

    try {
      await api.post("/start-meeting");
      setCommandState("success");
      setCommandMessage("Council convened. Backend acknowledged the start command.");
    } catch (error) {
      setCommandState("error");
      setCommandMessage("Failed to convene the council. Verify backend availability.");
    }
  };

  return (
    <main className="min-h-screen">
      <section className="mx-auto flex max-w-6xl flex-col gap-8 px-6 py-12">
        <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-8 shadow-2xl shadow-emerald-500/10">
          <p className="text-sm uppercase tracking-[0.35em] text-emerald-300">SOD Autonomous Corporation</p>
          <h1 className="mt-3 text-4xl font-bold sm:text-5xl">Command Center</h1>
          <p className="mt-4 max-w-3xl text-slate-300">
            A hardened offline-ready interface to supervise and activate the Python backend. Monitor live logs and
            dispatch mission-critical directives with confidence.
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3 text-slate-200">
                <span className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-300">
                  <Radio className="h-5 w-5" />
                </span>
                <div>
                  <p className="text-xs uppercase tracking-[0.25em] text-emerald-300">Live Console</p>
                  <p className="text-sm text-slate-400">Streaming updates from http://backend:8000/logs</p>
                </div>
              </div>
              {isLoadingLogs ? (
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Initializing feed…</span>
                </div>
              ) : null}
            </div>

            <div
              ref={consoleRef}
              className="mt-4 h-[28rem] rounded-2xl border border-slate-800 bg-black/70 p-4 font-mono text-sm text-emerald-200 shadow-inner"
            >
              {logError ? (
                <div className="flex h-full items-center justify-center text-center text-amber-200">{logError}</div>
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
          </div>

          <div className="flex flex-col gap-4 rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl shadow-emerald-500/5">
            <div className="space-y-2">
              <p className="text-xs uppercase tracking-[0.3em] text-emerald-300">Control Panel</p>
              <h2 className="text-2xl font-semibold">Operations</h2>
              <p className="text-sm text-slate-300">Issue directives to the backend orchestration service.</p>
            </div>

            <button
              type="button"
              onClick={handleStartMeeting}
              disabled={commandState === "running"}
              className="group inline-flex items-center justify-center gap-2 rounded-2xl bg-emerald-500 px-6 py-4 text-lg font-semibold text-slate-950 shadow-lg shadow-emerald-500/30 transition hover:scale-[1.01] hover:bg-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-300 focus:ring-offset-2 focus:ring-offset-slate-950 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {commandState === "running" ? <Loader2 className="h-5 w-5 animate-spin" /> : <Play className="h-5 w-5" />}
              CONVENE COUNCIL
            </button>

            {commandMessage ? (
              <div
                className={`rounded-xl border px-4 py-3 text-sm ${
                  commandState === "success"
                    ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-100"
                    : "border-amber-400/40 bg-amber-400/10 text-amber-100"
                }`}
              >
                {commandMessage}
              </div>
            ) : (
              <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4 text-xs text-slate-400">
                Press the button to send a POST request to <code className="text-slate-200">/start-meeting</code> on the
                backend service.
              </div>
            )}
          </div>
        </div>
      </section>
    </main>
  );
}
