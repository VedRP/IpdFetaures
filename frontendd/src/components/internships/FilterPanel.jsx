import { useState } from "react";
import { LOCATIONS, PERKS_OPTIONS, SOURCE_LABELS } from "../../data/internships";

function FilterSection({ title, expanded, onToggle, children }) {
  return (
    <div className="fp-section">
      <button type="button" className="fp-section-head" onClick={onToggle}>
        <span>{title}</span>
        <span>{expanded ? "▲" : "▼"}</span>
      </button>
      {expanded && <div className="fp-section-body">{children}</div>}
    </div>
  );
}

export function FilterPanel({
  filters,
  onUpdate,
  onReset,
  onToggleLocation,
  onTogglePerk,
  onAddSkill,
  onRemoveSkill,
  userSkills = [],
  sourceCounts = {},
}) {
  const [expanded, setExpanded] = useState({
    sortBy: true,
    source: true,
    stipend: true,
    location: true,
    duration: true,
    skills: true,
    perks: false,
  });
  const [skillDraft, setSkillDraft] = useState("");

  const toggle = (key) => setExpanded((prev) => ({ ...prev, [key]: !prev[key] }));

  const activeCount = [
    filters.stipendType !== "any",
    filters.locations.length > 0,
    filters.workFromHome,
    filters.durationMin > 1 || filters.durationMax < 12,
    filters.skills.length > 0,
    filters.perks.length > 0,
    filters.sources.length > 0,
  ].filter(Boolean).length;

  function submitSkill(e) {
    e.preventDefault();
    const v = skillDraft.trim();
    if (v) onAddSkill(v);
    setSkillDraft("");
  }

  return (
    <div className="fp-panel">
      <div className="fp-head">
        <div className="fp-head-left">
          <span>Filters</span>
          {activeCount > 0 && <span className="fp-count">{activeCount}</span>}
        </div>
        {activeCount > 0 && (
          <button type="button" className="fp-clear" onClick={onReset}>
            Clear all
          </button>
        )}
      </div>

      <FilterSection title="Sort By" expanded={expanded.sortBy} onToggle={() => toggle("sortBy")}>
        {["latest", "deadline", "stipend"].map((opt) => (
          <label className="fp-radio" key={opt}>
            <input
              type="radio"
              name="sortBy"
              checked={filters.sortBy === opt}
              onChange={() => onUpdate("sortBy", opt)}
            />
            <span>{opt === "latest" ? "Latest First" : opt === "deadline" ? "Deadline" : "Highest Stipend"}</span>
          </label>
        ))}
      </FilterSection>

      <FilterSection title="Source" expanded={expanded.source} onToggle={() => toggle("source")}>
        {Object.entries(SOURCE_LABELS)
          .filter(([key]) => sourceCounts[key] || filters.sources.includes(key))
          .map(([key, label]) => (
            <label className="fp-checkbox" key={key}>
              <input
                type="checkbox"
                checked={filters.sources.includes(key)}
                onChange={() =>
                  onUpdate(
                    "sources",
                    filters.sources.includes(key)
                      ? filters.sources.filter((s) => s !== key)
                      : [...filters.sources, key]
                  )
                }
              />
              <span className="fp-checkbox-label">{label}</span>
              <span className="fp-checkbox-count">{sourceCounts[key] ?? 0}</span>
            </label>
          ))}
      </FilterSection>

      <FilterSection title="Stipend" expanded={expanded.stipend} onToggle={() => toggle("stipend")}>
        {["any", "paid", "unpaid", "performance-based"].map((opt) => (
          <label className="fp-radio" key={opt}>
            <input
              type="radio"
              name="stipendType"
              checked={filters.stipendType === opt}
              onChange={() => onUpdate("stipendType", opt)}
            />
            <span>
              {opt === "any" ? "Any" : opt === "paid" ? "Paid" : opt === "unpaid" ? "Unpaid" : "Performance Based"}
            </span>
          </label>
        ))}
        {filters.stipendType === "paid" && (
          <div className="fp-range">
            <span className="fp-range-label">Stipend Range (₹/month)</span>
            <div className="fp-range-row">
              <input
                type="number"
                placeholder="Min"
                value={filters.stipendMin || ""}
                onChange={(e) => onUpdate("stipendMin", Number(e.target.value))}
              />
              <span>–</span>
              <input
                type="number"
                placeholder="Max"
                value={filters.stipendMax || ""}
                onChange={(e) => onUpdate("stipendMax", Number(e.target.value))}
              />
            </div>
          </div>
        )}
      </FilterSection>

      <FilterSection title="Location" expanded={expanded.location} onToggle={() => toggle("location")}>
        <div className="fp-scroll">
          {LOCATIONS.map((loc) => (
            <label className="fp-checkbox" key={loc}>
              <input
                type="checkbox"
                checked={filters.locations.includes(loc) || (loc === "Work from Home" && filters.workFromHome)}
                onChange={() =>
                  loc === "Work from Home" ? onUpdate("workFromHome", !filters.workFromHome) : onToggleLocation(loc)
                }
              />
              <span className="fp-checkbox-label">{loc}</span>
            </label>
          ))}
        </div>
      </FilterSection>

      <FilterSection title="Duration (months)" expanded={expanded.duration} onToggle={() => toggle("duration")}>
        <div className="fp-range-row">
          <input
            type="number"
            min={1}
            max={12}
            value={filters.durationMin}
            onChange={(e) => onUpdate("durationMin", Number(e.target.value))}
          />
          <span>–</span>
          <input
            type="number"
            min={1}
            max={12}
            value={filters.durationMax}
            onChange={(e) => onUpdate("durationMax", Number(e.target.value))}
          />
        </div>
        <p className="fp-range-caption">
          {filters.durationMin} – {filters.durationMax} months
        </p>
      </FilterSection>

      <FilterSection title="Skills" expanded={expanded.skills} onToggle={() => toggle("skills")}>
        <form onSubmit={submitSkill} className="fp-tag-input-row">
          <input
            placeholder="Add skill..."
            value={skillDraft}
            onChange={(e) => setSkillDraft(e.target.value)}
          />
        </form>
        {filters.skills.length > 0 && (
          <div className="fp-tag-list">
            {filters.skills.map((s) => (
              <span className="badge badge-neutral fp-tag" key={s} onClick={() => onRemoveSkill(s)}>
                {s} ×
              </span>
            ))}
          </div>
        )}
        {userSkills.length > 0 && (
          <button type="button" className="btn-secondary fp-use-skills" onClick={() => onUpdate("skills", userSkills)}>
            Use My Skills
          </button>
        )}
      </FilterSection>

      <FilterSection title="Perks" expanded={expanded.perks} onToggle={() => toggle("perks")}>
        <div className="fp-scroll">
          {PERKS_OPTIONS.map((perk) => (
            <label className="fp-checkbox" key={perk}>
              <input type="checkbox" checked={filters.perks.includes(perk)} onChange={() => onTogglePerk(perk)} />
              <span className="fp-checkbox-label">{perk}</span>
            </label>
          ))}
        </div>
      </FilterSection>
    </div>
  );
}
