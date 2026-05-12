import { useCallback, useEffect, useState } from "react";
import { Navigate, useNavigate, useParams } from "react-router-dom";

import {
  ApiError,
  fetchLeadActivity,
  fetchLeadV1,
  postLeadActivityNote,
  recomputeLeadRanking,
} from "../../api";
import type { ActivityItem } from "../../api/leadsV1";
import ActivityTimeline from "../../components/ActivityTimeline";
import LeadActivityNoteForm from "../../components/LeadActivityNoteForm";
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
  const [activityItems, setActivityItems] = useState<ActivityItem[]>([]);
  const [activityLoading, setActivityLoading] = useState(false);
  const [activityError, setActivityError] = useState<string | null>(null);

  const loadActivity = useCallback(async (id: string) => {
    setActivityLoading(true);
    setActivityError(null);
    try {
      const res = await fetchLeadActivity(id);
      setActivityItems(res.items);
    } catch (e) {
      const message =
        e instanceof ApiError
          ? e.detail ?? e.message
          : e instanceof Error
            ? e.message
            : "Failed to load activity";
      setActivityError(message);
      setActivityItems([]);
    } finally {
      setActivityLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!leadId) return;
    let cancelled = false;
    void (async () => {
      setLoadError(null);
      try {
        const data = await fetchLeadV1(leadId);
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

  useEffect(() => {
    if (!leadId || !lead) return;
    void loadActivity(leadId);
  }, [leadId, lead, loadActivity]);

  async function recomputeRanking() {
    if (!leadId) return;
    setIsWorking(true);
    try {
      await recomputeLeadRanking(leadId);
      const next = await fetchLeadV1(leadId);
      setLead(next);
      replaceLeadInList(next);
      await loadActivity(leadId);
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

  async function postNote(text: string) {
    if (!leadId) return;
    await postLeadActivityNote(leadId, text);
    await loadActivity(leadId);
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
      {activityError ? (
        <div className="card muted" role="alert">
          Activity: {activityError}
        </div>
      ) : null}
      <LeadDetails
        lead={lead}
        onBack={() => navigate("/leads")}
        onRecomputeRanking={() => void recomputeRanking()}
      />
      <ActivityTimeline items={activityItems} loading={activityLoading} />
      <LeadActivityNoteForm onSubmit={(t) => postNote(t)} disabled={isWorking} />
      {isWorking ? <div className="muted">Recomputing…</div> : null}
    </div>
  );
}
