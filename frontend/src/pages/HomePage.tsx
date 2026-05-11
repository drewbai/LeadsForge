import { useNavigate } from "react-router-dom";

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="stack">
      <div className="card">
        <h1>LeadsForge</h1>
        <p className="muted">
          Lead workspace UI — Phase 1 adds the app shell, routes, and navigation. Later phases connect
          search, API auth, metrics, subscriptions, and settings.
        </p>
        <div className="row split">
          <button type="button" onClick={() => navigate("/leads")}>
            Open leads (local demo)
          </button>
        </div>
      </div>
    </div>
  );
}
