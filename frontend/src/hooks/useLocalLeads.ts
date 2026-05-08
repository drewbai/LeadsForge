import { useEffect, useMemo, useState } from "react";

export type Lead = {
  id: string;
  name?: string;
  email?: string;
  company?: string;
  email_domain?: string;
  email_quality?: string;
  score?: number;
};

const STORAGE_KEY = "leadsforge.leads";

function safeParse(json: string | null): Lead[] {
  if (!json) return [];
  try {
    const parsed = JSON.parse(json);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter((x) => x && typeof x.id === "string") as Lead[];
  } catch {
    return [];
  }
}

export function useLocalLeads() {
  const [leads, setLeads] = useState<Lead[]>([]);

  useEffect(() => {
    setLeads(safeParse(localStorage.getItem(STORAGE_KEY)));
  }, []);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(leads));
  }, [leads]);

  function addLead(lead: Lead) {
    setLeads((prev) => [lead, ...prev]);
  }

  function updateLead(id: string, lead: Lead) {
    setLeads((prev) => prev.map((x) => (x.id === id ? lead : x)));
  }

  function deleteLead(id: string) {
    setLeads((prev) => prev.filter((x) => x.id !== id));
  }

  const byId = useMemo(() => new Map(leads.map((l) => [l.id, l])), [leads]);

  function getLead(id: string): Lead | undefined {
    return byId.get(id);
  }

  return { leads, addLead, updateLead, deleteLead, getLead };
}
