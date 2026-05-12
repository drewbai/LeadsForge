import type { Lead } from "../types/lead";

type LeadDetailsProps = {
  lead: Lead;
  onRecomputeRanking: () => void;
  onBack: () => void;
};

function dash(v: string | null | undefined): string {
  if (v === null || v === undefined || v === "") return "—";
  return v;
}

function row(label: string, value: string) {
  return (
    <div className="kv">
      <div className="k">{label}</div>
      <div className="v mono">{value}</div>
    </div>
  );
}

/** Display name: full_name if present, else short placeholder from email local-part. */
function displayName(lead: Lead): string {
  const fn = lead.full_name?.trim();
  if (fn) return fn;
  const at = lead.email.indexOf("@");
  if (at > 0) return lead.email.slice(0, at);
  return "—";
}

export default function LeadDetails(props: LeadDetailsProps) {
  const { lead } = props;

  return (
    <div className="card">
      <h2>Lead details</h2>

      {row("Name", displayName(lead))}
      {row("Email", lead.email)}
      {row("Company", dash(lead.company))}
      {row("Status", dash(lead.status))}
      {row("Source", lead.source)}
      {row("Created", lead.created_at)}
      {row("Updated", dash(lead.updated_at))}
      {row("id", lead.id)}
      {row("ranking_score", lead.ranking_score === null ? "—" : String(lead.ranking_score))}
      {row("ranking_explanation", lead.ranking_explanation ?? "—")}
      {row("last_ranked_at", lead.last_ranked_at ?? "—")}
      {row("assigned_to", lead.assigned_to ?? "—")}
      {row("routing_reason", lead.routing_reason ?? "—")}
      {row("last_routed_at", lead.last_routed_at ?? "—")}

      <div className="row split">
        <button type="button" onClick={props.onBack}>
          Back to list
        </button>
        <button type="button" onClick={props.onRecomputeRanking}>
          Recompute ranking
        </button>
      </div>
    </div>
  );
}
