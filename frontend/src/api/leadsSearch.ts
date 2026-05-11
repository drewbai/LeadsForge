import type { Lead } from "../types/lead";
import { apiGetJson, withQuery } from "./http";

export type LeadSearchParams = {
  text?: string;
  source?: string;
  limit?: number;
  offset?: number;
  sort_by?: string;
  sort_dir?: "asc" | "desc";
};

export type LeadSearchResponse = {
  results: Lead[];
  total: number;
  limit: number;
  offset: number;
};

/**
 * GET /api/v1/leads/search — server-side text search (email, source, ranking explanation)
 * plus optional source filter.
 */
export async function searchLeads(params: LeadSearchParams = {}): Promise<LeadSearchResponse> {
  const path = withQuery("/api/v1/leads/search", {
    text: params.text,
    source: params.source,
    limit: params.limit ?? 50,
    offset: params.offset ?? 0,
    sort_by: params.sort_by ?? "created_at",
    sort_dir: params.sort_dir ?? "desc",
  });
  return await apiGetJson<LeadSearchResponse>(path);
}
