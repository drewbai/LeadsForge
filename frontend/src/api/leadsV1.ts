import type { Lead } from "../types/lead";
import { apiGetJson, apiPostJson } from "./http";

export type ActivityItem = {
  id: string;
  lead_id: string;
  created_at: string;
  activity_type: string;
  activity_details: string | null;
  performed_by: string | null;
};

export type ActivityListResponse = {
  items: ActivityItem[];
};

/** Phase 4: canonical detail fetch under /api/v1/leads. */
export async function fetchLeadV1(leadId: string): Promise<Lead> {
  return await apiGetJson<Lead>(`/api/v1/leads/${leadId}`);
}

export async function fetchLeadActivity(leadId: string): Promise<ActivityListResponse> {
  return await apiGetJson<ActivityListResponse>(`/api/v1/leads/${leadId}/activity`);
}

export async function postLeadActivityNote(leadId: string, text: string): Promise<void> {
  await apiPostJson<{ status: string }, { text: string }>(`/api/v1/leads/${leadId}/activity`, { text });
}
