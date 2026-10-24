import { useState } from "react";
import { formatDuration, formatDate, formatStipend, sourceLabel } from "../../data/internships";
import { BookmarkIcon } from "../Icon";
import { accentColor } from "../../accentColors";

export function InternshipCard({ internship, isSaved = false, isApplied = false, onClick, onSave, onApply }) {
  const [saved, setSaved] = useState(isSaved);
  const [applied, setApplied] = useState(isApplied);

  const location = internship.isRemote
    ? "Work from Home"
    : [internship.city, internship.state].filter(Boolean).join(", ") || internship.country || "India";

  const deadlineSoon =
    internship.deadlineDate && new Date(internship.deadlineDate).getTime() - Date.now() < 7 * 86400000;

  function handleSave(e) {
    e.stopPropagation();
    setSaved((s) => !s);
    onSave?.(internship._id);
  }

  function handleApply(e) {
    e.stopPropagation();
    if (applied) return;
    setApplied(true);
    onApply?.(internship._id);
  }

  return (
    <div className="ic-card" onClick={onClick}>
      <div className="ic-body">
        <div className="ic-header">
          <div className="ic-header-main">
            <div className="ic-logo" style={{ background: accentColor(internship.company) }}>
              {internship.company?.[0] ?? "?"}
            </div>
            <div>
              <h3 className="ic-title">{internship.name}</h3>
              <p className="ic-subtitle">
                {internship.company} &middot; via {sourceLabel(internship.source)}
              </p>
            </div>
          </div>
          <button type="button" className={`ic-save${saved ? " active" : ""}`} onClick={handleSave}>
            <BookmarkIcon filled={saved} width={15} height={15} />
          </button>
        </div>

        <div className="ic-badges">
          {internship.isRemote && <span className="badge badge-success">Remote</span>}
          {deadlineSoon && <span className="badge badge-warning">Closing soon</span>}
        </div>

        <div className="ic-meta">
          <div>{location}</div>
          <div>
            <span className={internship.stipend?.type === "paid" ? "stipend-pill" : "stipend-plain"}>
              {formatStipend(internship.stipend)}
            </span>
          </div>
          <div>{formatDuration(internship.duration)}</div>
        </div>

        <div className="ic-skills">
          {internship.skills.slice(0, 3).map((s) => (
            <span className="badge badge-neutral" key={s}>
              {s}
            </span>
          ))}
          {internship.skills.length > 3 && (
            <span className="badge badge-outline">+{internship.skills.length - 3}</span>
          )}
        </div>

        {internship.deadlineDate && (
          <p className={`ic-deadline${deadlineSoon ? " soon" : ""}`}>Deadline: {formatDate(internship.deadlineDate)}</p>
        )}
      </div>

      <div className="ic-footer">
        <button type="button" className="btn-primary ic-apply" disabled={applied} onClick={handleApply}>
          <span>{applied ? "Applied" : "Apply"}</span>
          <span>{applied ? "✓" : "→"}</span>
        </button>
      </div>
    </div>
  );
}
