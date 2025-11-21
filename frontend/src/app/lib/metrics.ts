export type DailyCount = {
  date: string;
  count: number;
};

export type ChannelCount = {
  channel: string;
  count: number;
};

export type AnalyticsSummary = {
  pinkas_per_day: DailyCount[];
  missions_per_day: DailyCount[];
  messages_sent_per_channel: ChannelCount[];
};

const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL;
const isDev = process.env.NODE_ENV !== "production";

// The backend is expected to expose `/analytics/summary` with the above shape.
// If it is not yet implemented, the function will fall back to mocked data in development
// so that the UI remains usable while backend support is added.
async function fetchFromBackend(): Promise<AnalyticsSummary> {
  if (!BASE_URL) {
    throw new Error("NEXT_PUBLIC_BACKEND_URL is not configured for analytics");
  }

  const response = await fetch(`${BASE_URL}/analytics/summary`, {
    cache: "no-store",
    headers: {
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(
      `Analytics request failed: ${response.status} ${response.statusText}${message ? ` - ${message}` : ""}`,
    );
  }

  return (await response.json()) as AnalyticsSummary;
}

function buildMockAnalyticsSummary(): AnalyticsSummary {
  const today = new Date();
  const formatter = new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
  });

  const generateDaily = (base: number) =>
    Array.from({ length: 7 }, (_, index) => {
      const date = new Date(today);
      date.setDate(today.getDate() - (6 - index));
      return { date: formatter.format(date), count: Math.max(0, base + Math.round(Math.random() * 4 - 2)) };
    });

  return {
    pinkas_per_day: generateDaily(12),
    missions_per_day: generateDaily(6),
    messages_sent_per_channel: [
      { channel: "telegram", count: 42 },
      { channel: "whatsapp", count: 27 },
    ],
  };
}

export async function getAnalyticsSummary(): Promise<AnalyticsSummary> {
  try {
    return await fetchFromBackend();
  } catch (error) {
    if (isDev) {
      console.warn("Falling back to mocked analytics data:", error);
      return buildMockAnalyticsSummary();
    }
    throw error instanceof Error ? error : new Error("Unable to fetch analytics summary");
  }
}
