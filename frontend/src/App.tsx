import { useState } from "react";

import LeadDetails from "./components/LeadDetails";
import LeadForm from "./components/LeadForm";
import LeadList from "./components/LeadList";
import { enrichLead, reScoreLead, scoreLead } from "./api";
import type { Lead } from "./hooks/useLocalLeads";
import { useLocalLeads } from "./hooks/useLocalLeads";
import "./styles/app.css";
import "./styles/list.css";
import "./styles/nav.css";

export default function App() {
  const { leads, addLead, updateLead, deleteLead, getLead } = useLocalLeads();
  const [view, setView] = useState<"list" | "create" | "details">("list");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [isWorking, setIsWorking] = useState<boolean>(false);

  const selectedLead = selectedId ? getLead(selectedId) : undefined;

  async function createLead(raw: { name: string; email: string; company: string }) {
    const id = crypto.randomUUID();
    setIsWorking(true);
    try {
      const enriched = await enrichLead(raw);
      const scored = await scoreLead(enriched);
      const lead: Lead = { id, ...raw, ...enriched, ...scored };
      addLead(lead);
      setSelectedId(id);
      setView("details");
    } finally {
      setIsWorking(false);
    }
  }

  async function rescoreLead(lead: Lead) {
    setIsWorking(true);
    try {
      const scored = await reScoreLead(lead);
      const updated: Lead = { ...lead, ...scored };
      updateLead(lead.id, updated);
      setSelectedId(lead.id);
      setView("details");
    } finally {
      setIsWorking(false);
    }
  }

  return (
    <div className="app">
      <div className="nav">
        <div className="navInner">
          <div className="brand">LeadsForge</div>
          <div className="navActions">
            <button type="button" onClick={() => setView("list")} disabled={isWorking}>
              Lead List
            </button>
            <button type="button" onClick={() => setView("create")} disabled={isWorking}>
              Create Lead
            </button>
          </div>
        </div>
      </div>

      <div className="container">
        {view === "list" ? (
          <LeadList
            leads={leads}
            onSelect={(id) => {
              setSelectedId(id);
              setView("details");
            }}
            onDelete={(id) => {
              deleteLead(id);
              if (selectedId === id) setSelectedId(null);
              setView("list");
            }}
          />
        ) : view === "create" ? (
          <div className="stack">
            <LeadForm onCreate={createLead} />
            {isWorking ? <div className="muted">Working...</div> : null}
          </div>
        ) : selectedLead ? (
          <div className="stack">
            <LeadDetails
              lead={selectedLead}
              onBack={() => setView("list")}
              onRescore={(lead) => rescoreLead(lead)}
            />
            {isWorking ? <div className="muted">Working...</div> : null}
          </div>
        ) : (
          <div className="card">
            <h2>Lead Details</h2>
            <div className="muted">Lead not found.</div>
            <div className="row">
              <button type="button" onClick={() => setView("list")}>
                Back to List
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
