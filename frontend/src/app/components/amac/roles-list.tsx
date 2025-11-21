import type { AmacRole } from "@/app/lib/amac_api";

interface RolesListProps {
  roles: AmacRole[];
}

export default function RolesList({ roles }: RolesListProps) {
  return (
    <div className="overflow-hidden rounded-xl border border-white/10 bg-slate-900/50">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-white/5">
          <thead className="bg-slate-900/80">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-400">
                Internal Name
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-400">
                Display Name
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-400">Tribe</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-400">
                Mission
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {roles.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-center text-sm text-slate-400">
                  No roles available.
                </td>
              </tr>
            ) : (
              roles.map((role) => (
                <tr key={role.internal_name} className="transition hover:bg-white/5">
                  <td className="whitespace-nowrap px-4 py-3 text-sm font-medium text-white">{role.internal_name}</td>
                  <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-100">{role.display_name}</td>
                  <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-100">{role.tribe}</td>
                  <td className="px-4 py-3 text-sm text-slate-100">{role.mission}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
