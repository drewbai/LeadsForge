import type { Lead } from "../hooks/useLocalLeads";

type LeadListProps = {
  leads: Lead[];
  onSelect: (leadId: string) => void;
  onDelete: (leadId: string) => void;
};

export default function LeadList(props: LeadListProps) {
  return (
    <div className="card">
      <h2>Lead List</h2>

      {props.leads.length === 0 ? (
        <div className="muted">No saved leads yet.</div>
      ) : (
        <div className="tableWrap">
          <table className="leadTable">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Score</th>
                <th className="actionsCol">Actions</th>
              </tr>
            </thead>
            <tbody>
              {props.leads.map((lead) => (
                <tr key={lead.id}>
                  <td>{lead.name ?? ""}</td>
                  <td className="mono">{lead.email ?? ""}</td>
                  <td className="mono">{lead.score ?? ""}</td>
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
