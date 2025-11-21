export type AmacRole = {
  internal_name: string;
  display_name: string;
  tribe: string;
  mission: string;
};

export type AmacProposal = {
  id: string;
  title: string;
  status: string;
  budget_ton: number | null;
  created_at: string;
};

const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL;
const isDev = process.env.NODE_ENV !== "production";

// The backend is expected to expose `/amac/roles` in a future iteration.
// Until it is available, the function falls back to a mocked roles registry in development
// so the UI remains functional.
async function fetchRolesFromBackend(): Promise<AmacRole[]> {
  if (!BASE_URL) {
    throw new Error("NEXT_PUBLIC_BACKEND_URL is not configured for AMAC roles");
  }

  const response = await fetch(`${BASE_URL}/amac/roles`, {
    cache: "no-store",
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(
      `AMAC roles request failed: ${response.status} ${response.statusText}${message ? ` - ${message}` : ""}`,
    );
  }

  return (await response.json()) as AmacRole[];
}

function buildMockRoles(): AmacRole[] {
  return [
    {
      internal_name: "master_of_coin",
      display_name: "Master of Coin",
      tribe: "Finance",
      mission: "Oversees TON budgeting and treasury allocations.",
    },
    {
      internal_name: "guardian_of_protocols",
      display_name: "Guardian of Protocols",
      tribe: "Operations",
      mission: "Ensures protocol compliance across autonomous agents.",
    },
    {
      internal_name: "custodian_of_records",
      display_name: "Custodian of Records",
      tribe: "Governance",
      mission: "Maintains Pinkas integrity and archival standards.",
    },
  ];
}

export async function fetchAmacRoles(): Promise<AmacRole[]> {
  try {
    return await fetchRolesFromBackend();
  } catch (error) {
    if (isDev) {
      console.warn("Falling back to mocked AMAC roles:", error);
      return buildMockRoles();
    }
    throw error instanceof Error ? error : new Error("Unable to fetch AMAC roles");
  }
}

async function fetchProposalsFromBackend(): Promise<AmacProposal[]> {
  if (!BASE_URL) {
    throw new Error("NEXT_PUBLIC_BACKEND_URL is not configured for AMAC proposals");
  }

  const response = await fetch(`${BASE_URL}/admin/amac/proposals`, {
    cache: "no-store",
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(
      `AMAC proposals request failed: ${response.status} ${response.statusText}${message ? ` - ${message}` : ""}`,
    );
  }

  return (await response.json()) as AmacProposal[];
}

function buildMockProposals(): AmacProposal[] {
  const now = new Date();
  const formatDate = (date: Date) => date.toISOString();

  return [
    {
      id: "prop-001",
      title: "Emergency responder mission for BotNet Gamma",
      status: "approved",
      budget_ton: 1200,
      created_at: formatDate(new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000)),
    },
    {
      id: "prop-002",
      title: "Upgrade CPAO adjudication heuristics",
      status: "needs_revision",
      budget_ton: 600,
      created_at: formatDate(new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)),
    },
    {
      id: "prop-003",
      title: "Deploy AMAC liaison for Mission Control",
      status: "rejected",
      budget_ton: null,
      created_at: formatDate(new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000)),
    },
  ];
}

export async function fetchAmacProposals(): Promise<AmacProposal[]> {
  try {
    return await fetchProposalsFromBackend();
  } catch (error) {
    if (isDev) {
      console.warn("Falling back to mocked AMAC proposals:", error);
      return buildMockProposals();
    }
    throw error instanceof Error ? error : new Error("Unable to fetch AMAC proposals");
  }
}
