import { useNavigate } from "react-router-dom";

type PlaceholderPageProps = {
  title: string;
  phase: number;
  description?: string;
};

export default function PlaceholderPage({ title, phase, description }: PlaceholderPageProps) {
  const navigate = useNavigate();

  return (
    <div className="stack">
      <div className="card">
        <h1>{title}</h1>
        <p className="muted">
          {description ?? `This area is reserved for UI Phase ${phase} of the roadmap.`}
        </p>
        <div className="row">
          <button type="button" onClick={() => navigate("/")}>
            Back to home
          </button>
        </div>
      </div>
    </div>
  );
}
