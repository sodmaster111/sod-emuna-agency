import ProposalsTable from "@/app/components/amac/proposals-table";
import RolesList from "@/app/components/amac/roles-list";
import { fetchAmacProposals, fetchAmacRoles } from "@/app/lib/amac_api";

export default async function AmacDashboardPage() {
  let error: string | null = null;
  let roles: Awaited<ReturnType<typeof fetchAmacRoles>> = [];
  let proposals: Awaited<ReturnType<typeof fetchAmacProposals>> = [];

  try {
    [roles, proposals] = await Promise.all([fetchAmacRoles(), fetchAmacProposals()]);
  } catch (err) {
    error = err instanceof Error ? err.message : "Failed to load AMAC data";
  }

  if (error) {
    return (
      <div className="space-y-3 rounded-xl border border-rose-400/40 bg-rose-950/40 p-6 text-rose-100">
        <p className="font-semibold">AMAC data unavailable</p>
        <p className="text-sm text-rose-200/80">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-10">
      <header className="space-y-2">
        <h2 className="text-2xl font-semibold text-white">AMAC Governance</h2>
        <p className="text-sm text-slate-300">
          Review Autonomous Mission Authority Council roles and proposals, including board decisions and budget
          allocations.
        </p>
      </header>

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-white">Roles</h3>
          <p className="text-xs uppercase tracking-wide text-slate-400">Roles registry</p>
        </div>
        <RolesList roles={roles} />
      </section>

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-white">Proposals</h3>
          <p className="text-xs uppercase tracking-wide text-slate-400">Board decisions</p>
        </div>
        <ProposalsTable proposals={proposals} />
      </section>
    </div>
  );
}
