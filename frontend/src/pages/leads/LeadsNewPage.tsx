import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { enrichLead, scoreLead } from "../../api";
import LeadForm from "../../components/LeadForm";
import { useLocalLeadsContext } from "../../context/LocalLeadsContext";
import type { Lead } from "../../hooks/useLocalLeads";

export default function LeadsNewPage() {
  const navigate = useNavigate();
  const { addLead } = useLocalLeadsContext();
  const [isWorking, setIsWorking] = useState(false);

  async function createLead(raw: { name: string; email: string; company: string }) {
    const id = crypto.randomUUID();
    setIsWorking(true);
    try {
      const enriched = await enrichLead(raw);
      const scored = await scoreLead(enriched);
      const lead: Lead = { id, ...raw, ...enriched, ...scored };
      addLead(lead);
      navigate(`/leads/${id}`);
    } finally {
      setIsWorking(false);
    }
  }

  return (
    <div className="stack">
      <div className="row split">
        <h2 className="pageTitle">Create lead</h2>
        <button type="button" onClick={() => navigate("/leads")} disabled={isWorking}>
          Cancel
        </button>
      </div>
      <LeadForm onCreate={createLead} />
      {isWorking ? <div className="muted">Working...</div> : null}
    </div>
  );
}
