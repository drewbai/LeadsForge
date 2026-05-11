import { apiPostJsonRaw } from "./http";

/** Triggers server-side ranking recompute for a lead (async pipeline may still run). */
export async function recomputeLeadRanking(leadId: string): Promise<unknown> {
  return await apiPostJsonRaw(`/api/v1/ranking/${leadId}/recompute`);
}
