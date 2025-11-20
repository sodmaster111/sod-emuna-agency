"use client";

import { useState } from "react";
import { Loader2, Play } from "lucide-react";

import api from "@/lib/api";

export type CommandState = "idle" | "running" | "success" | "error";

export interface OperationsPanelProps {
  title?: string;
  description?: string;
  actionLabel?: string;
  endpoint?: string;
  successMessage?: string;
  errorMessage?: string;
}

export function OperationsPanel({
  title = "Operations",
  description = "Issue directives to the backend orchestration service.",
  actionLabel = "Convene Council",
  endpoint = "/start-meeting",
  successMessage = "Council convened. Backend acknowledged the start command.",
  errorMessage = "Failed to convene the council. Verify backend availability.",
}: OperationsPanelProps) {
  const [commandState, setCommandState] = useState<CommandState>("idle");
  const [commandMessage, setCommandMessage] = useState<string | null>(null);

  const handleAction = async () => {
    setCommandState("running");
    setCommandMessage(null);

    try {
      await api.post(endpoint);
      setCommandState("success");
      setCommandMessage(successMessage);
    } catch (err) {
      setCommandState("error");
      setCommandMessage(errorMessage);
    }
  };

  return (
    <div className="flex h-full flex-col gap-4 rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl shadow-emerald-500/5">
      <div className="space-y-2">
        <p className="text-xs uppercase tracking-[0.3em] text-emerald-300">Control Panel</p>
        <h2 className="text-2xl font-semibold">{title}</h2>
        <p className="text-sm text-slate-300">{description}</p>
      </div>

      <button
        type="button"
        onClick={handleAction}
        disabled={commandState === "running"}
        className="group inline-flex items-center justify-center gap-2 rounded-2xl bg-emerald-500 px-6 py-4 text-lg font-semibold text-slate-950 shadow-lg shadow-emerald-500/30 transition hover:scale-[1.01] hover:bg-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-300 focus:ring-offset-2 focus:ring-offset-slate-950 disabled:cursor-not-allowed disabled:opacity-70"
      >
        {commandState === "running" ? <Loader2 className="h-5 w-5 animate-spin" /> : <Play className="h-5 w-5" />}
        {actionLabel.toUpperCase()}
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
          Press the button to send a POST request to <code className="text-slate-200">{endpoint}</code> on the backend service.
        </div>
      )}
    </div>
  );
}
