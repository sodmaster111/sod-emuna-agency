import type { AmacProposal } from "@/app/lib/amac_api";

interface ProposalsTableProps {
  proposals: AmacProposal[];
}

const statusStyles: Record<string, string> = {
  approved: "bg-emerald-500/15 text-emerald-200 ring-1 ring-emerald-500/40",
  rejected: "bg-rose-500/15 text-rose-200 ring-1 ring-rose-500/40",
  needs_revision: "bg-amber-500/15 text-amber-100 ring-1 ring-amber-500/40",
  pending: "bg-slate-500/15 text-slate-100 ring-1 ring-slate-500/40",
};

function formatBudget(budget: number | null): string {
  if (budget === null || Number.isNaN(budget)) return "—";
  return `${budget.toLocaleString()} TON`;
}

function formatDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

export default function ProposalsTable({ proposals }: ProposalsTableProps) {
  return (
    <div className="overflow-hidden rounded-xl border border-white/10 bg-slate-900/50">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-white/5">
          <thead className="bg-slate-900/80">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-400">Title</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-400">Status</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-400">
                Budget (TON)
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-400">
                Created At
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {proposals.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-center text-sm text-slate-400">
                  No proposals found.
                </td>
              </tr>
            ) : (
              proposals.map((proposal) => {
                const badgeClass = statusStyles[proposal.status] ?? statusStyles.pending;
                return (
                  <tr key={proposal.id} className="transition hover:bg-white/5">
                    <td className="px-4 py-3 text-sm font-medium text-white">{proposal.title}</td>
                    <td className="px-4 py-3 text-sm text-slate-100">
                      <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold uppercase ${badgeClass}`}>
                        {proposal.status.replace("_", " ")}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-100">{formatBudget(proposal.budget_ton)}</td>
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-100">{formatDate(proposal.created_at)}</td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
