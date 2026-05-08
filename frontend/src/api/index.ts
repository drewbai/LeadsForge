const ENRICH_URL = "http://localhost:8000/enrichment/single";
const SCORE_URL = "http://localhost:8000/scoring/single";

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
