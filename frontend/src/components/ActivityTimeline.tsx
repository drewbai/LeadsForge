import type { ActivityItem } from "../api/leadsV1";

type ActivityTimelineProps = {
  items: ActivityItem[];
  loading: boolean;
};

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

function formatDetails(item: ActivityItem): string {
  if (item.activity_details) return item.activity_details;
  return "—";
}

export default function ActivityTimeline(props: ActivityTimelineProps) {
  return (
    <div className="card">
      <h2 className="activityTimelineTitle">Activity timeline</h2>
      {props.loading ? <div className="muted">Loading activity…</div> : null}
      {!props.loading && props.items.length === 0 ? (
        <div className="muted">No activity yet. Add a note below or trigger system events.</div>
      ) : null}
      {!props.loading && props.items.length > 0 ? (
        <ul className="activityTimelineList">
          {props.items.map((item) => (
            <li key={item.id} className="activityTimelineItem">
              <div className="activityTimelineMeta">
                <span className="mono activityTimelineType">{item.activity_type}</span>
                <span className="muted activityTimelineWhen">{formatTime(item.created_at)}</span>
              </div>
              <div className="activityTimelineBody">{formatDetails(item)}</div>
              {item.performed_by ? (
                <div className="muted activityTimelineActor">by {item.performed_by}</div>
              ) : null}
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
