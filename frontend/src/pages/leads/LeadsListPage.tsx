import { useNavigate } from "react-router-dom";

import LeadList from "../../components/LeadList";
import { useLeadsContext } from "../../context/LeadsContext";

export default function LeadsListPage() {
  const navigate = useNavigate();
  const { leads, loading, error, refresh, deleteLead } = useLeadsContext();

  return (
    <div className="stack">
      <div className="row split">
        <h2 className="pageTitle">Leads</h2>
        <button type="button" onClick={() => navigate("/leads/new")}>
          Create lead
        </button>
      </div>

      {error ? (
        <div className="card stack">
          <div className="muted">Could not load leads: {error}</div>
          <div className="row">
            <button type="button" onClick={() => void refresh()}>
              Retry
            </button>
          </div>
        </div>
      ) : null}

      {loading ? <div className="muted">Loading leads…</div> : null}

      {!loading ? (
        <LeadList
          leads={leads}
          onSelect={(id) => navigate(`/leads/${id}`)}
          onDelete={(id) => {
            void (async () => {
              await deleteLead(id);
              navigate("/leads", { replace: true });
            })();
          }}
        />
      ) : null}
    </div>
  );
}
