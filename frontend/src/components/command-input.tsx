"use client";

import { FormEvent, useState } from "react";
import { API_BASE_URL } from "@/lib/config";

export default function CommandInput() {
  const [command, setCommand] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submitCommand = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!command.trim()) return;

    setBusy(true);
    setStatus(null);

    try {
      const response = await fetch(`${API_BASE_URL}/command`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command })
      });

      if (!response.ok) {
        throw new Error("Command failed");
      }

      setStatus("Command dispatched to the orchestrator");
      setCommand("");
    } catch (error) {
      console.error(error);
      setStatus("Unable to reach orchestrator. Please retry.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <form onSubmit={submitCommand} className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4 shadow-xl">
      <div className="mb-2 flex items-center justify-between">
        <div>
          <p className="text-sm uppercase tracking-wide text-slate-400">Orchestrator</p>
          <p className="text-lg font-semibold text-white">Send a directive</p>
        </div>
        {status && <span className="text-xs text-emerald-300">{status}</span>}
      </div>
      <textarea
        value={command}
        onChange={(e) => setCommand(e.target.value)}
        placeholder="Instruct the CEO agent..."
        className="h-32 w-full resize-none rounded-xl border border-slate-700 bg-slate-950/70 p-3 text-sm text-white placeholder:text-slate-500 focus:border-emerald-400 focus:outline-none"
      />
      <div className="mt-3 flex justify-end">
        <button
          type="submit"
          disabled={busy}
          className="inline-flex items-center gap-2 rounded-full bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400 disabled:opacity-60"
        >
          {busy ? "Sending..." : "Send command"}
        </button>
      </div>
    </form>
  );
}
