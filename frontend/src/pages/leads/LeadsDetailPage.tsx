import { useState } from "react";
import { Navigate, useNavigate, useParams } from "react-router-dom";

import { reScoreLead } from "../../api";
import LeadDetails from "../../components/LeadDetails";
import { useLocalLeadsContext } from "../../context/LocalLeadsContext";
import type { Lead } from "../../hooks/useLocalLeads";

export default function LeadsDetailPage() {
  const { leadId } = useParams<{ leadId: string }>();
  const navigate = useNavigate();
  const { getLead, updateLead } = useLocalLeadsContext();
  const [isWorking, setIsWorking] = useState(false);

  const lead = leadId ? getLead(leadId) : undefined;

  async function rescore(leadToScore: Lead) {
    setIsWorking(true);
    try {
      const scored = await reScoreLead(leadToScore);
      const updated: Lead = { ...leadToScore, ...scored };
      updateLead(leadToScore.id, updated);
    } finally {
      setIsWorking(false);
    }
  }

  if (!leadId) {
    return <Navigate to="/leads" replace />;
  }

  if (!lead) {
    return (
      <div className="card stack">
        <h2>Lead Details</h2>
        <div className="muted">Lead not found.</div>
        <div className="row">
          <button type="button" onClick={() => navigate("/leads")}>
            Back to list
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="stack">
      <LeadDetails lead={lead} onBack={() => navigate("/leads")} onRescore={rescore} />
      {isWorking ? <div className="muted">Working...</div> : null}
    </div>
  );
}
