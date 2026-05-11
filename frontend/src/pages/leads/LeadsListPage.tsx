import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { ApiError, searchLeads } from "../../api";
import LeadList from "../../components/LeadList";
import { useLeadsContext } from "../../context/LeadsContext";
import type { Lead } from "../../types/lead";

const SEARCH_DEBOUNCE_MS = 350;
const PAGE_LIMIT = 50;

export default function LeadsListPage() {
  const navigate = useNavigate();
  const { deleteLead } = useLeadsContext();

  const [textInput, setTextInput] = useState("");
  const [sourceInput, setSourceInput] = useState("");
  const [debouncedText, setDebouncedText] = useState("");
  const [debouncedSource, setDebouncedSource] = useState("");
  const [retryKey, setRetryKey] = useState(0);

  const [rows, setRows] = useState<Lead[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const t = window.setTimeout(() => {
      setDebouncedText(textInput.trim());
      setDebouncedSource(sourceInput.trim());
    }, SEARCH_DEBOUNCE_MS);
    return () => window.clearTimeout(t);
  }, [textInput, sourceInput]);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await searchLeads({
          text: debouncedText || undefined,
          source: debouncedSource || undefined,
          limit: PAGE_LIMIT,
          offset: 0,
        });
        if (!cancelled) {
          setRows(data.results);
          setTotal(data.total);
        }
      } catch (e) {
        if (!cancelled) {
          const message =
            e instanceof ApiError
              ? e.detail ?? e.message
              : e instanceof Error
                ? e.message
                : "Search failed";
          setError(message);
          setRows([]);
          setTotal(0);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [debouncedText, debouncedSource, retryKey]);

  const hasFilters = debouncedText.length > 0 || debouncedSource.length > 0;
  const showingTo = rows.length === 0 ? 0 : Math.min(total, rows.length);
  const resultHint =
    !loading && !error && total > 0
      ? `Showing 1–${showingTo} of ${total}${total > PAGE_LIMIT ? ` (limit ${PAGE_LIMIT})` : ""}`
      : null;

  const emptyMessage = hasFilters
    ? "No leads match your filters. Try different search text or source."
    : "No leads yet. Create one to get started.";

  function refetch() {
    setRetryKey((k) => k + 1);
  }

  return (
    <div className="stack">
      <div className="row split">
        <h2 className="pageTitle">Leads</h2>
        <button type="button" onClick={() => navigate("/leads/new")}>
          Create lead
        </button>
      </div>

      <div className="card stack leadSearchCard">
        <div className="muted">
          Search uses the API (email, source, ranking explanation). Results update as you type.
        </div>
        <div className="leadSearchGrid">
          <label className="field">
            <span className="label">Search</span>
            <input
              type="search"
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="e.g. domain, source name, explanation text…"
              autoComplete="off"
              aria-label="Search leads"
            />
          </label>
          <label className="field">
            <span className="label">Source equals</span>
            <input
              value={sourceInput}
              onChange={(e) => setSourceInput(e.target.value)}
              placeholder="Exact source value"
              autoComplete="off"
              aria-label="Filter by source"
            />
          </label>
        </div>
      </div>

      {error ? (
        <div className="card stack">
          <div className="muted">Could not load results: {error}</div>
          <div className="row">
            <button type="button" onClick={refetch}>
              Retry
            </button>
          </div>
        </div>
      ) : null}

      {loading ? <div className="muted">Loading…</div> : null}

      {!loading && !error ? (
        <LeadList
          leads={rows}
          onSelect={(id) => navigate(`/leads/${id}`)}
          emptyMessage={emptyMessage}
          resultHint={resultHint ?? undefined}
          onDelete={(id) => {
            void (async () => {
              await deleteLead(id);
              navigate("/leads", { replace: true });
              try {
                const data = await searchLeads({
                  text: debouncedText || undefined,
                  source: debouncedSource || undefined,
                  limit: PAGE_LIMIT,
                  offset: 0,
                });
                setRows(data.results);
                setTotal(data.total);
              } catch {
                refetch();
              }
            })();
          }}
        />
      ) : null}
    </div>
  );
}
