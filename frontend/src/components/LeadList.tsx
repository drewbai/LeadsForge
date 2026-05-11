import type { Lead } from "../types/lead";

type LeadListProps = {
  leads: Lead[];
  onSelect: (leadId: string) => void;
  onDelete: (leadId: string) => void;
  /** Shown when `leads.length === 0` */
  emptyMessage?: string;
  /** e.g. "Showing 1–50 of 240" */
  resultHint?: string;
};

function formatRank(score: number | null): string {
  if (score === null || Number.isNaN(score)) return "—";
  return String(score);
}

function formatWhen(iso: string): string {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

export default function LeadList(props: LeadListProps) {
  const emptyMessage =
    props.emptyMessage ?? "No leads yet. Create one to get started.";

  return (
    <div className="card">
      <div className="leadListHeader">
        <h2 className="leadListTitle">Lead list</h2>
        {props.resultHint ? <span className="muted">{props.resultHint}</span> : null}
      </div>

      {props.leads.length === 0 ? (
        <div className="muted">{emptyMessage}</div>
      ) : (
        <div className="tableWrap">
          <table className="leadTable">
            <thead>
              <tr>
                <th>Email</th>
                <th>Source</th>
                <th>Rank</th>
                <th>Created</th>
                <th className="actionsCol">Actions</th>
              </tr>
            </thead>
            <tbody>
              {props.leads.map((lead) => (
                <tr key={lead.id}>
                  <td className="mono">{lead.email}</td>
                  <td>{lead.source}</td>
                  <td className="mono">{formatRank(lead.ranking_score)}</td>
                  <td className="muted">{formatWhen(lead.created_at)}</td>
                  <td className="actionsCol">
                    <div className="actions">
                      <button type="button" onClick={() => props.onSelect(lead.id)}>
                        View
                      </button>
                      <button
                        type="button"
                        className="danger"
                        onClick={() => props.onDelete(lead.id)}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
