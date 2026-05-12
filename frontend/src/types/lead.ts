/** Mirrors backend ``LeadRead`` JSON (snake_case). */
export type Lead = {
  id: string;
  email: string;
  source: string;
  created_at: string;
  full_name?: string | null;
  company?: string | null;
  status?: string | null;
  updated_at?: string | null;
  ranking_score: number | null;
  ranking_explanation: string | null;
  last_ranked_at: string | null;
  assigned_to: string | null;
  routing_reason: string | null;
  last_routed_at: string | null;
};
