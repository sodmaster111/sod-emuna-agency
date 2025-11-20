"use client";

import { useEffect, useRef, useState } from "react";
import { API_BASE_URL } from "@/lib/config";

export default function MeetingLog() {
  const [entries, setEntries] = useState<string[]>([]);
  const [status, setStatus] = useState<string>("Connecting to meeting stream...");
  const logRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let retryInterval: NodeJS.Timeout | undefined;
    let eventSource: EventSource | undefined;

    const connectStream = () => {
      if (eventSource) {
        eventSource.close();
      }

      try {
        const streamUrl = `${API_BASE_URL}/meeting/logs/stream`;
        const source = new EventSource(streamUrl);
        eventSource = source;

        source.onopen = () => setStatus("Live board meeting feed");
        source.onmessage = (event) => {
          if (event.data) {
            setEntries((prev) => [...prev, event.data]);
          }
        };
        source.onerror = () => {
          setStatus("Stream unavailable. Retrying with periodic fetch...");
          source.close();
          startPollingFallback();
        };
      } catch (error) {
        console.error("SSE unavailable", error);
        startPollingFallback();
      }
    };

    const startPollingFallback = () => {
      if (retryInterval) {
        clearInterval(retryInterval);
      }
      retryInterval = setInterval(async () => {
        try {
          const response = await fetch(`${API_BASE_URL}/meeting/logs`);
          if (!response.ok) {
            throw new Error("Failed to fetch logs");
          }
          const payload = await response.json();
          if (Array.isArray(payload)) {
            setEntries(payload);
            setStatus("Polling meeting transcript");
          }
        } catch (pollError) {
          setStatus("Unable to reach meeting feed");
          console.error(pollError);
        }
      }, 4000);
    };

    connectStream();

    return () => {
      if (eventSource) {
        eventSource.close();
      }
      if (retryInterval) {
        clearInterval(retryInterval);
      }
    };
  }, []);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [entries]);

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4 shadow-xl">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <p className="text-sm uppercase tracking-wide text-slate-400">Board meeting log</p>
          <p className="text-lg font-semibold text-white">Live updates</p>
        </div>
        <span className="flex items-center gap-2 text-xs text-emerald-300">
          <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
          {status}
        </span>
      </div>
      <div
        ref={logRef}
        className="h-64 overflow-y-auto rounded-xl bg-slate-950/60 p-4 text-sm text-slate-100 ring-1 ring-slate-800"
      >
        {entries.length === 0 ? (
          <p className="text-slate-500">Waiting for the board to speak...</p>
        ) : (
          entries.map((entry, index) => (
            <p key={`${entry}-${index}`} className="whitespace-pre-wrap leading-relaxed text-slate-200">
              {entry}
            </p>
          ))
        )}
      </div>
    </div>
  );
}
