import { useEffect, useState } from "react";

import { ApiError, apiGetJson } from "../api/http";
import AboutCard from "../components/AboutCard";

type AboutApi = {
  backend_poetry_version: string;
  git_commit: string | null;
};

function kvRow(label: string, value: string) {
  return (
    <div className="kv">
      <div className="k">{label}</div>
      <div className="v mono">{value}</div>
    </div>
  );
}

export default function AboutPage() {
  const [about, setAbout] = useState<AboutApi | null>(null);
  const [aboutError, setAboutError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const data = await apiGetJson<AboutApi>("/api/v1/about");
        if (!cancelled) {
          setAbout(data);
          setAboutError(null);
        }
      } catch (e) {
        if (!cancelled) {
          const msg =
            e instanceof ApiError
              ? e.detail ?? e.message
              : e instanceof Error
                ? e.message
                : "Unknown error";
          setAboutError(msg);
          setAbout(null);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const apiBase = (import.meta.env.VITE_API_BASE_URL ?? "").trim();
  const viteMode = import.meta.env.MODE;
  const frontendCommit = (import.meta.env.VITE_BUILD_COMMIT ?? "").trim();
  const backendCommit = about?.git_commit?.trim() ?? "";

  return (
    <div className="stack aboutStack">
      <h1 className="pageTitle">About</h1>

      <AboutCard title="LeadsForge">
        <p className="muted aboutTightTop">
          LeadsForge is a lightweight lead intelligence and workflow engine.
        </p>
        <p className="muted aboutTightBottom">© 2026 LeadsForge</p>
      </AboutCard>

      <AboutCard title="Versions">
        <p className="muted aboutTightTop">
          UI Phase 3: lead list uses <span className="mono">GET /api/v1/leads/search</span> (debounced text +
          source filter).
        </p>
        {kvRow("Frontend (package.json)", __LF_FRONTEND_PKG_VERSION__)}
        {kvRow(
          "Backend (pyproject.toml · Poetry)",
          about ? about.backend_poetry_version : aboutError ? `— (${aboutError})` : "—",
        )}
      </AboutCard>

      <AboutCard title="Environment">
        {kvRow("Vite mode (NODE_ENV-like)", viteMode)}
        {kvRow("VITE_API_BASE_URL", apiBase || "— (empty: same-origin / dev proxy)")}
      </AboutCard>

      <AboutCard title="Build">
        {kvRow("Frontend commit (VITE_BUILD_COMMIT*)", frontendCommit || "—")}
        {kvRow("Backend commit (LEADSFORGE_GIT_COMMIT)**", backendCommit || "—")}
        <p className="muted aboutFootnote">
          *Set at build time in <span className="mono">.env</span> or CI. **Set where the API runs.
        </p>
      </AboutCard>
    </div>
  );
}
