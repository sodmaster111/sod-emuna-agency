
"use client";

import { useEffect, useRef, useState } from "react";
import { BadgeCheck, Loader2, Play, Radio, WifiOff } from "lucide-react";

import { DailyWidget } from "@/app/components/ritual/DailyWidget";

import api from "@/lib/api";

const HEALTH_POLL_INTERVAL = 2000;
const LOG_POLL_INTERVAL = 2000;
const DEFAULT_MISSION_GOAL = "Devise the next operational steps for the Digital Sanhedrin";

type CommandState = "idle" | "running" | "success" | "error";

type LogEntry = string;

type MissionResponse = {
  status?: string;
};

type HealthResponse = {
  status?: string;
};

type BackendState = "checking" | "online" | "offline";

export default function CommandCenterPage() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isLoadingLogs, setIsLoadingLogs] = useState(true);
  const [logError, setLogError] = useState<string | null>(null);
  const [backendStatus, setBackendStatus] = useState<BackendState>("checking");
  const [backendMessage, setBackendMessage] = useState("Verifying connection…");
  const [commandState, setCommandState] = useState<CommandState>("idle");
  const [commandMessage, setCommandMessage] = useState<string | null>(null);
  const consoleRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let isMounted = true;

    const fetchLogs = async () => {
      try {
        const response = await api.get("/api/v1/logs");
        if (!isMounted) return;

        const data = response.data;
        const formatted: string[] = Array.isArray(data)
          ? data.map((entry) => (typeof entry === "string" ? entry : JSON.stringify(entry)))
          : typeof data === "string"
            ? data.split(/\n+/).filter(Boolean)
            : [];

        setLogs(formatted);
        setLogError(null);
      } catch (error) {
        if (!isMounted) return;
        setLogError("Backend unreachable. Retrying automatically.");
      } finally {
        if (isMounted) {
          setIsLoadingLogs(false);
        }
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, LOG_POLL_INTERVAL);

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

  useEffect(() => {
    let isMounted = true;

    const checkBackend = async () => {
      try {
        const response = await api.get<HealthResponse>("/health");
        if (!isMounted) return;

        const reportedStatus = response.data?.status || "Operational";
        setBackendStatus("online");
        setBackendMessage(reportedStatus);
      } catch (error) {
        if (!isMounted) return;
        setBackendStatus("offline");
        setBackendMessage("Backend unreachable");
      }
    };

    checkBackend();
    const interval = setInterval(checkBackend, HEALTH_POLL_INTERVAL);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const handleStartMeeting = async () => {
    setCommandState("running");
    setCommandMessage(null);

    try {
      const response = await api.post<MissionResponse>("/api/v1/mission", {
        goal: DEFAULT_MISSION_GOAL,
      });

      setCommandState("success");
      setCommandMessage(
        response.data?.status === "running"
          ? "Council already active. Mission loop confirmed running."
          : "Council convened. Backend acknowledged the start command.",
      );
    } catch (error) {
      setCommandState("error");
      setCommandMessage("Failed to convene the council. Verify backend availability.");
    }
  };

  const backendIndicator = (() => {
    if (backendStatus === "online") {
      return (
        <span className="inline-flex items-center gap-2 rounded-full bg-emerald-500/15 px-3 py-1 text-xs font-semibold text-emerald-200">
          <BadgeCheck className="h-4 w-4" /> Online
        </span>
      );
    }

    if (backendStatus === "offline") {
      return (
        <span className="inline-flex items-center gap-2 rounded-full bg-amber-500/15 px-3 py-1 text-xs font-semibold text-amber-200">
          <WifiOff className="h-4 w-4" /> Backend Unreachable
        </span>
      );
    }

    return (
      <span className="inline-flex items-center gap-2 rounded-full bg-slate-500/15 px-3 py-1 text-xs font-semibold text-slate-200">
        <Loader2 className="h-4 w-4 animate-spin" /> Checking…
      </span>
    );
  })();

  return (
    <main className="min-h-screen">
      <section className="mx-auto flex max-w-6xl flex-col gap-8 px-6 py-12">
        <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-8 shadow-2xl shadow-emerald-500/10">
          <p className="text-sm uppercase tracking-[0.35em] text-emerald-300">SOD Autonomous Corporation</p>
          <div className="mt-3 flex flex-wrap items-center gap-3">
            <h1 className="text-4xl font-bold sm:text-5xl">Command Center</h1>
            {backendIndicator}
          </div>
          <p className="mt-4 max-w-3xl text-slate-300">
            A hardened offline-ready interface to supervise and activate the Python backend. Monitor live logs and
            dispatch mission-critical directives with confidence.
          </p>
        </div>

        <section className="rounded-3xl border border-slate-800 bg-slate-950/60 p-4 shadow-lg shadow-emerald-500/10">
          <DailyWidget />
        </section>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3 text-slate-200">
                <span className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-300">
                  <Radio className="h-5 w-5" />
                </span>
                <div>
                  <p className="text-xs uppercase tracking-[0.25em] text-emerald-300">Live Logs</p>
                  <p className="text-sm text-slate-400">Streaming updates from /api/v1/logs</p>
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

            <div className="rounded-2xl border border-slate-800 bg-slate-950/50 p-4 text-sm text-slate-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-emerald-300">Backend Status</p>
                  <p className="text-lg font-semibold text-white">{backendMessage}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-slate-400">Connection</p>
                  {backendIndicator}
                </div>
              </div>
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
                Press the button to send a POST request to <code className="text-slate-200">/api/v1/mission</code> on the
                backend service.
              </div>
            )}
          </div>
        </div>
      </section>
    </main>
  );
}
