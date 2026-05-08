const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000").replace(
  /\/$/,
  "",
);

const ENRICH_URL = `${API_BASE}/enrichment/single`;
const SCORE_URL = `${API_BASE}/scoring/single`;

async function postJson(url: string, body: unknown): Promise<any> {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return await res.json();
}

export async function enrichLead(lead: any): Promise<any> {
  return await postJson(ENRICH_URL, { lead });
}

export async function scoreLead(lead: any): Promise<any> {
  return await postJson(SCORE_URL, { lead });
}

export async function reScoreLead(lead: any): Promise<any> {
  return await postJson(SCORE_URL, { lead });
}
