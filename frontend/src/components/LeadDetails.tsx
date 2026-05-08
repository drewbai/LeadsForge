import type { Lead } from "../hooks/useLocalLeads";

type LeadDetailsProps = {
  lead: Lead;
  onRescore: (lead: Lead) => void;
  onBack: () => void;
};

export default function LeadDetails(props: LeadDetailsProps) {
  const lead = props.lead;

  return (
    <div className="card">
      <h2>Lead Details</h2>

      <div className="kv">
        <div className="k">id</div>
        <div className="v mono">{lead.id}</div>
      </div>
      <div className="kv">
        <div className="k">name</div>
        <div className="v">{String(lead.name ?? "")}</div>
      </div>
      <div className="kv">
        <div className="k">email</div>
        <div className="v mono">{String(lead.email ?? "")}</div>
      </div>
      <div className="kv">
        <div className="k">company</div>
        <div className="v">{String(lead.company ?? "")}</div>
      </div>

      {lead.email_domain !== undefined && (
        <div className="kv">
          <div className="k">email_domain</div>
          <div className="v mono">{String(lead.email_domain ?? "")}</div>
        </div>
      )}
      {lead.email_quality !== undefined && (
        <div className="kv">
          <div className="k">email_quality</div>
          <div className="v mono">{String(lead.email_quality ?? "")}</div>
        </div>
      )}
      {lead.score !== undefined && (
        <div className="kv">
          <div className="k">score</div>
          <div className="v mono">{String(lead.score ?? "")}</div>
        </div>
      )}

      <div className="row split">
        <button type="button" onClick={props.onBack}>
          Back to List
        </button>
        <button type="button" onClick={() => props.onRescore(lead)}>
          Re-score Lead
        </button>
      </div>
    </div>
  );
}
