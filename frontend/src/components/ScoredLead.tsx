type ScoredLeadProps = {
  lead: any;
};

export default function ScoredLead(props: ScoredLeadProps) {
  const lead = props.lead ?? {};

  return (
    <div className="card">
      <h2>Scored</h2>

      <div className="kv">
        <div className="k">score</div>
        <div className="v">{String(lead.score ?? "")}</div>
      </div>

      <div className="kv">
        <div className="k">email_domain</div>
        <div className="v">{String(lead.email_domain ?? "")}</div>
      </div>
      <div className="kv">
        <div className="k">email_quality</div>
        <div className="v">{String(lead.email_quality ?? "")}</div>
      </div>
    </div>
  );
}
