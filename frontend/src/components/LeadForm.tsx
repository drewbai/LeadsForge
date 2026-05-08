import { useState } from "react";

type LeadFormProps = {
  onCreate: (lead: { name: string; email: string; company: string }) => void;
};

export default function LeadForm(props: LeadFormProps) {
  const [name, setName] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [company, setCompany] = useState<string>("");

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    props.onCreate({ name, email, company });
  }

  return (
    <form className="card" onSubmit={onSubmit}>
      <h2>Lead</h2>

      <label className="field">
        <span className="label">Name</span>
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Jane Doe" />
      </label>

      <label className="field">
        <span className="label">Email</span>
        <input
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="jane@example.com"
        />
      </label>

      <label className="field">
        <span className="label">Company</span>
        <input
          value={company}
          onChange={(e) => setCompany(e.target.value)}
          placeholder="Acme Inc."
        />
      </label>

      <div className="row">
        <button type="submit">Create Lead</button>
      </div>
    </form>
  );
}
