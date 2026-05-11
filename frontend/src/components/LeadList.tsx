import type { Lead } from "../types/lead";

type LeadListProps = {
  leads: Lead[];
  onSelect: (leadId: string) => void;
  onDelete: (leadId: string) => void;
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
  return (
    <div className="card">
      <h2>Lead list</h2>

      {props.leads.length === 0 ? (
        <div className="muted">No leads yet. Create one to get started.</div>
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
