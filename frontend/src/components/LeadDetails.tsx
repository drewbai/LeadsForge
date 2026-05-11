import type { Lead } from "../types/lead";

type LeadDetailsProps = {
  lead: Lead;
  onRecomputeRanking: () => void;
  onBack: () => void;
};

function row(label: string, value: string) {
  return (
    <div className="kv">
      <div className="k">{label}</div>
      <div className="v mono">{value}</div>
    </div>
  );
}

export default function LeadDetails(props: LeadDetailsProps) {
  const { lead } = props;

  return (
    <div className="card">
      <h2>Lead details</h2>

      {row("id", lead.id)}
      {row("email", lead.email)}
      {row("source", lead.source)}
      {row("created_at", lead.created_at)}
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
