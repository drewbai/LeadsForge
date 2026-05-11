import type { Lead } from "../types/lead";
import { apiDelete, apiGetJson, apiPostJson } from "./http";

export type LeadCreateBody = {
  email: string;
  source: string;
};

export async function fetchLeads(): Promise<Lead[]> {
  return await apiGetJson<Lead[]>("/leads/");
}

export async function createLead(body: LeadCreateBody): Promise<Lead> {
  return await apiPostJson<Lead, LeadCreateBody>("/leads/", body);
}

export async function fetchLead(leadId: string): Promise<Lead> {
  return await apiGetJson<Lead>(`/leads/${leadId}`);
}

export async function deleteLead(leadId: string): Promise<void> {
  await apiDelete(`/leads/${leadId}`);
}
