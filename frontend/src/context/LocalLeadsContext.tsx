import { createContext, useContext, type ReactNode } from "react";

import type { Lead } from "../hooks/useLocalLeads";
import { useLocalLeads } from "../hooks/useLocalLeads";

export type LocalLeadsApi = {
  leads: Lead[];
  addLead: (lead: Lead) => void;
  updateLead: (id: string, lead: Lead) => void;
  deleteLead: (id: string) => void;
  getLead: (id: string) => Lead | undefined;
};

const LocalLeadsContext = createContext<LocalLeadsApi | null>(null);

export function LocalLeadsProvider({ children }: { children: ReactNode }) {
  const api = useLocalLeads();
  return <LocalLeadsContext.Provider value={api}>{children}</LocalLeadsContext.Provider>;
}

export function useLocalLeadsContext(): LocalLeadsApi {
  const ctx = useContext(LocalLeadsContext);
  if (!ctx) {
    throw new Error("useLocalLeadsContext must be used within LocalLeadsProvider");
  }
  return ctx;
}
