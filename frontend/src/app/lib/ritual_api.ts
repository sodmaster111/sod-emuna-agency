const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL;

export type DayInfo = {
  gregorian_date: string;
  jewish_date_str: string;
  parsha?: string | null;
  day_type: string;
};

export async function fetchDayInfo(lang?: string): Promise<DayInfo> {
  if (!API_BASE) {
    throw new Error("NEXT_PUBLIC_BACKEND_URL is not configured for the frontend");
  }

  const url = new URL(`${API_BASE}/ritual/day-info`);
  if (lang) {
    url.searchParams.set("lang", lang);
  }

  const response = await fetch(url.toString(), {
    headers: {
      Accept: "application/json",
    },
    // TODO: remove cache override if backend provides proper cache headers
    cache: "no-store",
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(
      `Failed to fetch day info: ${response.status} ${response.statusText}${message ? ` - ${message}` : ""}`,
    );
  }

  return (await response.json()) as DayInfo;
}
