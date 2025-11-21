import Link from "next/link";
import type { PinkasEntry } from "@/app/lib/api";

interface PinkasTableProps {
  entries: PinkasEntry[];
  loading?: boolean;
  onRowClick?: (id: number) => void;
}

export default function PinkasTable({ entries, loading = false, onRowClick }: PinkasTableProps) {
  return (
    <div className="overflow-hidden rounded-xl border border-white/10 bg-slate-900/50">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-white/5">
          <thead className="bg-slate-900/80">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-400">
                Timestamp
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-400">
                Agent
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-400">
                Action
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-400">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {loading ? (
              <tr>
                <td colSpan={4} className="px-4 py-8 text-center text-sm text-slate-300">
                  Loading Pinkas entries...
                </td>
              </tr>
            ) : entries.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-center text-sm text-slate-400">
                  No entries found for the selected filters.
                </td>
              </tr>
            ) : (
              entries.map((entry) => {
                const content = (
                  <tr
                    key={entry.id}
                    className="cursor-pointer transition hover:bg-white/5"
                    onClick={() => onRowClick?.(entry.id)}
                  >
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-white">{entry.timestamp}</td>
                    <td className="px-4 py-3 text-sm text-slate-200">{entry.agent}</td>
                    <td className="px-4 py-3 text-sm text-slate-200">{entry.action}</td>
                    <td className="px-4 py-3 text-sm">
                      <span className="rounded-full bg-white/5 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-slate-100">
                        {entry.status}
                      </span>
                    </td>
                  </tr>
                );

                if (!onRowClick) {
                  return (
                    <Link key={entry.id} href={`/dashboard/pinkas/${entry.id}`} className="contents">
                      {content}
                    </Link>
                  );
                }

                return content;
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
