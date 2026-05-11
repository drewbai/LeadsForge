import { useNavigate } from "react-router-dom";

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="stack">
      <div className="card">
        <h1>LeadsForge</h1>
        <p className="muted">
          Phase 2 connects the leads workspace to the FastAPI backend: list, create, detail, delete, and
          ranking recompute. Run the API on port 8000 (Vite proxies API routes in dev), then open Leads.
        </p>
        <div className="row split">
          <button type="button" onClick={() => navigate("/leads")}>
            Open leads
          </button>
        </div>
      </div>
    </div>
  );
}
