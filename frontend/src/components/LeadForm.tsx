import { useState } from "react";

type LeadFormProps = {
  defaultSource?: string;
  onCreate: (lead: { email: string; source: string }) => void;
};

export default function LeadForm(props: LeadFormProps) {
  const { defaultSource = "manual-ui" } = props;
  const [email, setEmail] = useState<string>("");
  const [source, setSource] = useState<string>(defaultSource);

  function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    props.onCreate({ email: email.trim(), source: source.trim() || defaultSource });
  }

  return (
    <form className="card" onSubmit={onSubmit}>
      <h2>New lead</h2>
      <p className="muted">
        Leads are stored in the API (email + source). Ranking runs on the server after create.
      </p>

      <label className="field">
        <span className="label">Email</span>
        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="jane@example.com"
        />
      </label>

      <label className="field">
        <span className="label">Source</span>
        <input
          value={source}
          onChange={(e) => setSource(e.target.value)}
          placeholder="campaign, referral, csv, …"
        />
      </label>

      <div className="row">
        <button type="submit">Create lead</button>
      </div>
    </form>
  );
}
