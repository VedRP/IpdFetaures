import { useState } from "react";
import PageHeader from "../../components/PageHeader";
import { CheckIcon, FlagIcon } from "../../components/Icon";

const QUEUE = [
  {
    id: "q1",
    title: "Data Entry Executive",
    company: "QuickCash Ventures",
    decision: "block",
    reason: "Upfront registration fee requested",
  },
  {
    id: "q2",
    title: "Social Media Intern",
    company: "Glow Media Co.",
    decision: "review",
    reason: "Generic title + unusually high opening count",
  },
  {
    id: "q3",
    title: "Backend Engineering Intern",
    company: "HeliT Consulting",
    decision: "review",
    reason: "New company, no prior history",
  },
  {
    id: "q4",
    title: "Frontend Engineering Intern",
    company: "Acme Robotics",
    decision: "clear",
    reason: "Verified company, consistent posting history",
  },
];

const DECISION_META = {
  block: { label: "Block", badgeClass: "badge-urgent" },
  review: { label: "Needs review", badgeClass: "badge-warning" },
  clear: { label: "Clear", badgeClass: "badge-success" },
};

export default function InternshipQueue({ section = "02", title = "Internship Queue" }) {
  const [queue, setQueue] = useState(QUEUE);

  function resolve(id, status) {
    setQueue((prev) => prev.map((item) => (item.id === id ? { ...item, resolved: status } : item)));
  }

  const pending = queue.filter((item) => !item.resolved);

  return (
    <>
      <PageHeader step={section} title={title} />

      <div className="label" style={{ marginBottom: 14 }}>
        {pending.length} pending &middot; {queue.length - pending.length} resolved this session
      </div>

      <div className="mod-queue">
        {queue.map((item) => {
          const meta = DECISION_META[item.decision];
          return (
            <div className={`mod-queue-row${item.resolved ? " resolved" : ""}`} key={item.id}>
              <div className="mod-queue-main">
                <div className="mod-queue-title">{item.title}</div>
                <div className="mod-queue-company">{item.company}</div>
                <div className="mod-queue-reason">{item.reason}</div>
              </div>
              <span className={`badge ${meta.badgeClass}`}>{meta.label}</span>
              {item.resolved ? (
                <span className="pill mod-queue-resolved-tag">{item.resolved}</span>
              ) : (
                <div className="mod-queue-actions">
                  <button type="button" className="btn-secondary mod-approve" onClick={() => resolve(item.id, "Approved")}>
                    <CheckIcon width={13} height={13} /> Approve
                  </button>
                  <button type="button" className="btn-secondary mod-reject" onClick={() => resolve(item.id, "Rejected")}>
                    <FlagIcon width={13} height={13} /> Reject
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </>
  );
}
