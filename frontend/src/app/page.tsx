import { ServerDrivenDashboard } from "@/components/server-driven-dashboard";
import { dashboardSections } from "@/lib/dashboard-schema";

export default function CommandCenterPage() {
  return (
    <main className="min-h-screen">
      <ServerDrivenDashboard sections={dashboardSections} />
    </main>
  );
}
