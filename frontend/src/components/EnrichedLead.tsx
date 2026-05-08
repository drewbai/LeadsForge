type EnrichedLeadProps = {
  lead: any;
  onScore: () => void;
};

export default function EnrichedLead(props: EnrichedLeadProps) {
  const lead = props.lead ?? {};

  return (
    <div className="card">
      <h2>Enriched</h2>

      <div className="kv">
        <div className="k">email_domain</div>
        <div className="v">{String(lead.email_domain ?? "")}</div>
      </div>
      <div className="kv">
        <div className="k">email_quality</div>
        <div className="v">{String(lead.email_quality ?? "")}</div>
      </div>

      <div className="row">
        <button type="button" onClick={props.onScore}>
          Score Lead
        </button>
      </div>
    </div>
  );
}
