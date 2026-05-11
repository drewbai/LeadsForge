import { useEffect, useState } from "react";
import { Navigate, useNavigate, useParams } from "react-router-dom";

import { ApiError, fetchLead, recomputeLeadRanking } from "../../api";
import LeadDetails from "../../components/LeadDetails";
import { useLeadsContext } from "../../context/LeadsContext";
import type { Lead } from "../../types/lead";

export default function LeadsDetailPage() {
  const { leadId } = useParams<{ leadId: string }>();
  const navigate = useNavigate();
  const { replaceLeadInList } = useLeadsContext();
  const [lead, setLead] = useState<Lead | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [isWorking, setIsWorking] = useState(false);

  useEffect(() => {
    if (!leadId) return;
    let cancelled = false;
    void (async () => {
      setLoadError(null);
      try {
        const data = await fetchLead(leadId);
        if (!cancelled) setLead(data);
      } catch (e) {
        if (!cancelled) {
          const message =
            e instanceof ApiError
              ? e.detail ?? e.message
              : e instanceof Error
                ? e.message
                : "Lead not found";
          setLoadError(message);
          setLead(null);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [leadId]);

  async function recomputeRanking() {
    if (!leadId) return;
    setIsWorking(true);
    try {
      await recomputeLeadRanking(leadId);
      const next = await fetchLead(leadId);
      setLead(next);
      replaceLeadInList(next);
    } catch (e) {
      const message =
        e instanceof ApiError
          ? e.detail ?? e.message
          : e instanceof Error
            ? e.message
            : "Recompute failed";
      setLoadError(message);
    } finally {
      setIsWorking(false);
    }
  }

  if (!leadId) {
    return <Navigate to="/leads" replace />;
  }

  if (loadError && !lead) {
    return (
      <div className="card stack">
        <h2>Lead details</h2>
        <div className="muted">{loadError}</div>
        <div className="row">
          <button type="button" onClick={() => navigate("/leads")}>
            Back to list
          </button>
        </div>
      </div>
    );
  }

  if (!lead) {
    return (
      <div className="stack">
        <div className="muted">Loading lead…</div>
      </div>
    );
  }

  return (
    <div className="stack">
      {loadError ? (
        <div className="card muted" role="alert">
          {loadError}
        </div>
      ) : null}
      <LeadDetails
        lead={lead}
        onBack={() => navigate("/leads")}
        onRecomputeRanking={() => void recomputeRanking()}
      />
      {isWorking ? <div className="muted">Recomputing…</div> : null}
    </div>
  );
}
