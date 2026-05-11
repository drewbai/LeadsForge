import { useNavigate } from "react-router-dom";

import LeadList from "../../components/LeadList";
import { useLocalLeadsContext } from "../../context/LocalLeadsContext";

export default function LeadsListPage() {
  const navigate = useNavigate();
  const { leads, deleteLead } = useLocalLeadsContext();

  return (
    <div className="stack">
      <div className="row split">
        <h2 className="pageTitle">Leads</h2>
        <button type="button" onClick={() => navigate("/leads/new")}>
          Create lead
        </button>
      </div>
      <LeadList
        leads={leads}
        onSelect={(id) => navigate(`/leads/${id}`)}
        onDelete={(id) => {
          deleteLead(id);
          navigate("/leads", { replace: true });
        }}
      />
    </div>
  );
}
