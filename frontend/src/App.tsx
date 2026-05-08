import { useState } from "react";

import EnrichedLead from "./components/EnrichedLead";
import LeadForm from "./components/LeadForm";
import ScoredLead from "./components/ScoredLead";
import { scoreLead } from "./api";
import "./styles/app.css";

export default function App() {
  const [rawLead, setRawLead] = useState<any | null>(null);
  const [enrichedLead, setEnrichedLead] = useState<any | null>(null);
  const [scoredLead, setScoredLead] = useState<any | null>(null);

  async function onScore() {
    if (!enrichedLead) return;
    const scored = await scoreLead(enrichedLead);
    setScoredLead(scored);
  }

  return (
    <div className="app">
      <div className="container">
        <h1 className="title">LeadsForge</h1>

        {!enrichedLead ? (
          <LeadForm
            onEnriched={(lead) => {
              setRawLead(lead);
              setEnrichedLead(lead);
              setScoredLead(null);
            }}
          />
        ) : !scoredLead ? (
          <EnrichedLead lead={enrichedLead} onScore={onScore} />
        ) : (
          <ScoredLead lead={scoredLead} />
        )}

        {/* rawLead is kept for the deterministic state machine; not displayed yet */}
        <div style={{ display: "none" }}>{rawLead ? "has-raw" : "no-raw"}</div>
      </div>
    </div>
  );
}
