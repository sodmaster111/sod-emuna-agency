// API client for the Command Center dashboard.
// NOTE: Ensure NEXT_PUBLIC_BACKEND_URL is set to the backend service (e.g. http://backend:8000 in Docker or a production URL).

export type HealthResponse = {
  status: string;
  services?: {
    database?: string;
    celery?: string;
    [key: string]: string | undefined;
  };
  [key: string]: unknown;
};

export type PinkasEntry = {
  id: number;
  timestamp: string;
  agent: string;
  action: string;
  status: string;
  details?: string;
  payload?: unknown;
  result?: unknown;
};

export type PinkasListResponse = {
  items: PinkasEntry[];
  total?: number;
  limit?: number;
  offset?: number;
};

export type ScheduleCommandBody = {
  agent_name: string;
  payload: unknown;
};

export type ScheduleCommandResponse = {
  task_id: string;
  message?: string;
};

export type CommandStatusResponse = {
  task_id: string;
  state: string;
  summary?: string;
  detail?: string;
  result?: unknown;
};

const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  if (!BASE_URL) {
    throw new Error("NEXT_PUBLIC_BACKEND_URL is not configured for the frontend");
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(
      `API request failed: ${response.status} ${response.statusText}${message ? ` - ${message}` : ""}`,
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export async function getHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>("/health/deep");
}

export async function getPinkas(params: {
  limit?: number;
  offset?: number;
  agent?: string;
  status?: string;
} = {}): Promise<PinkasListResponse> {
  const searchParams = new URLSearchParams();

  if (params.limit) searchParams.append("limit", String(params.limit));
  if (params.offset) searchParams.append("offset", String(params.offset));
  if (params.agent) searchParams.append("agent", params.agent);
  if (params.status) searchParams.append("status", params.status);

  const query = searchParams.toString();
  const path = `/pinkas${query ? `?${query}` : ""}`;
  return apiFetch<PinkasListResponse>(path);
}

export async function getPinkasById(id: number): Promise<PinkasEntry> {
  return apiFetch<PinkasEntry>(`/pinkas/${id}`);
}

export async function scheduleCommand(body: ScheduleCommandBody): Promise<ScheduleCommandResponse> {
  return apiFetch<ScheduleCommandResponse>("/commands/schedule", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function getCommandStatus(task_id: string): Promise<CommandStatusResponse> {
  return apiFetch<CommandStatusResponse>(`/commands/status/${task_id}`);
}
