import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";

import { ApiError, createLead as apiCreateLead, deleteLead as apiDeleteLead, fetchLeads } from "../api";
import type { Lead } from "../types/lead";

export type LeadsContextValue = {
  leads: Lead[];
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  createLead: (input: { email: string; source: string }) => Promise<Lead>;
  deleteLead: (id: string) => Promise<void>;
  replaceLeadInList: (lead: Lead) => void;
};

const LeadsContext = createContext<LeadsContextValue | null>(null);

export function LeadsProvider({ children }: { children: ReactNode }) {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const next = await fetchLeads();
      setLeads(next);
    } catch (e) {
      const message =
        e instanceof ApiError
          ? e.detail ?? e.message
          : e instanceof Error
            ? e.message
            : "Failed to load leads";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const createLead = useCallback(async (input: { email: string; source: string }) => {
    const lead = await apiCreateLead(input);
    setLeads((prev) => [lead, ...prev.filter((l) => l.id !== lead.id)]);
    return lead;
  }, []);

  const deleteLead = useCallback(async (id: string) => {
    await apiDeleteLead(id);
    setLeads((prev) => prev.filter((l) => l.id !== id));
  }, []);

  const replaceLeadInList = useCallback((lead: Lead) => {
    setLeads((prev) => prev.map((l) => (l.id === lead.id ? lead : l)));
  }, []);

  const value: LeadsContextValue = {
    leads,
    loading,
    error,
    refresh,
    createLead,
    deleteLead,
    replaceLeadInList,
  };

  return <LeadsContext.Provider value={value}>{children}</LeadsContext.Provider>;
}

export function useLeadsContext(): LeadsContextValue {
  const ctx = useContext(LeadsContext);
  if (!ctx) {
    throw new Error("useLeadsContext must be used within LeadsProvider");
  }
  return ctx;
}
