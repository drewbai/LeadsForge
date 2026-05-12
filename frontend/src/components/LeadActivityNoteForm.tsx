import { useState } from "react";

type LeadActivityNoteFormProps = {
  disabled?: boolean;
  onSubmit: (text: string) => void | Promise<void>;
};

export default function LeadActivityNoteForm(props: LeadActivityNoteFormProps) {
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const t = text.trim();
    if (!t || busy || props.disabled) return;
    setBusy(true);
    try {
      await props.onSubmit(t);
      setText("");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="card" onSubmit={(e) => void handleSubmit(e)}>
      <h2 className="activityNoteTitle">Add note</h2>
      <label className="field fieldTightTop">
        <span className="label">Note</span>
        <textarea
          className="activityNoteTextarea"
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={3}
          placeholder="Internal note (persisted to activity log)"
          disabled={busy || props.disabled}
          aria-label="Activity note text"
        />
      </label>
      <div className="row">
        <button type="submit" disabled={busy || props.disabled || !text.trim()}>
          {busy ? "Saving…" : "Post note"}
        </button>
      </div>
    </form>
  );
}
