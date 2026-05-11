import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { ApiError } from "../../api";
import LeadForm from "../../components/LeadForm";
import { useLeadsContext } from "../../context/LeadsContext";

export default function LeadsNewPage() {
  const navigate = useNavigate();
  const { createLead } = useLeadsContext();
  const [isWorking, setIsWorking] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  async function handleCreate(raw: { email: string; source: string }) {
    setFormError(null);
    setIsWorking(true);
    try {
      const lead = await createLead(raw);
      navigate(`/leads/${lead.id}`);
    } catch (e) {
      const message =
        e instanceof ApiError
          ? e.detail ?? e.message
          : e instanceof Error
            ? e.message
            : "Could not create lead";
      setFormError(message);
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
      {formError ? (
        <div className="card muted" role="alert">
          {formError}
        </div>
      ) : null}
      <LeadForm onCreate={handleCreate} />
      {isWorking ? <div className="muted">Saving…</div> : null}
    </div>
  );
}
