import { notFound } from "next/navigation";
import { getPinkasById } from "@/app/lib/api";

export default async function PinkasDetailPage({ params }: { params: { id: string } }) {
  const entryId = Number(params.id);

  if (Number.isNaN(entryId)) {
    notFound();
  }

  try {
    const entry = await getPinkasById(entryId);

    return (
      <div className="space-y-4">
        <div className="space-y-1">
          <h2 className="text-2xl font-semibold text-white">Pinkas Entry #{entry.id}</h2>
          <p className="text-sm text-slate-300">Captured at {entry.timestamp}</p>
        </div>

        <dl className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div className="rounded-lg border border-white/10 bg-slate-900/60 p-4">
            <dt className="text-xs uppercase tracking-wide text-slate-400">Agent</dt>
            <dd className="text-lg font-semibold text-white">{entry.agent}</dd>
          </div>
          <div className="rounded-lg border border-white/10 bg-slate-900/60 p-4">
            <dt className="text-xs uppercase tracking-wide text-slate-400">Status</dt>
            <dd className="text-lg font-semibold text-white">{entry.status}</dd>
          </div>
          <div className="rounded-lg border border-white/10 bg-slate-900/60 p-4 md:col-span-2">
            <dt className="text-xs uppercase tracking-wide text-slate-400">Action</dt>
            <dd className="text-sm text-slate-100">{entry.action}</dd>
          </div>
          {entry.details && (
            <div className="rounded-lg border border-white/10 bg-slate-900/60 p-4 md:col-span-2">
              <dt className="text-xs uppercase tracking-wide text-slate-400">Details</dt>
              <dd className="text-sm text-slate-100 whitespace-pre-wrap">{entry.details}</dd>
            </div>
          )}
          {entry.payload && (
            <div className="rounded-lg border border-white/10 bg-slate-900/60 p-4 md:col-span-2">
              <dt className="text-xs uppercase tracking-wide text-slate-400">Payload</dt>
              <dd>
                <pre className="overflow-x-auto whitespace-pre-wrap break-words text-xs text-slate-200">
                  {JSON.stringify(entry.payload, null, 2)}
                </pre>
              </dd>
            </div>
          )}
          {entry.result && (
            <div className="rounded-lg border border-white/10 bg-slate-900/60 p-4 md:col-span-2">
              <dt className="text-xs uppercase tracking-wide text-slate-400">Result</dt>
              <dd>
                <pre className="overflow-x-auto whitespace-pre-wrap break-words text-xs text-slate-200">
                  {JSON.stringify(entry.result, null, 2)}
                </pre>
              </dd>
            </div>
          )}
        </dl>
      </div>
    );
  } catch {
    notFound();
  }
}
