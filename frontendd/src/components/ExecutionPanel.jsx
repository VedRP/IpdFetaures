const DEFAULT_TAGS = [
  { code: "R", color: "var(--color-tag-blue)", name: "Research", meta: "Primary · 0.4x" },
  { code: "I", color: "var(--color-tag-purple)", name: "Prior Art", meta: "Primary + fallback" },
  { code: "F", color: "var(--color-tag-green)", name: "Feasibility", meta: "Primary · 0.4x" },
];

export default function ExecutionPanel({
  eyebrow = "AUTONOMOUS ROUTER",
  heading = "Capability planner",
  budget = "Budget: 0.06 USDC",
  waves = "2 waves",
  tags = DEFAULT_TAGS,
  gateTitle = "Evidence quality gate",
  gateMeta = "Schema · citations · confidence · conflicts",
}) {
  return (
    <div>
      <div className="breadcrumb" style={{ marginBottom: 10 }}>
        <span className="path">Execution Route</span>
        <span className="status" style={{ color: "var(--color-ink-soft)" }}>
          {waves}
        </span>
      </div>

      <div className="card-dark">
        <div className="card-dark-header">
          <div className="eyebrow">{eyebrow}</div>
          <h3>{heading}</h3>
          <div className="budget">{budget}</div>
        </div>

        <div className="tag-grid">
          {tags.map((tag) => (
            <div className="tag-card" key={tag.code}>
              <div className="tag-square" style={{ background: tag.color }}>
                {tag.code}
              </div>
              <div className="name">{tag.name}</div>
              <div className="meta">{tag.meta}</div>
            </div>
          ))}
        </div>

        <div className="gate-row">
          <div className="gate-diamond" />
          <div>
            <div className="title">{gateTitle}</div>
            <div className="meta">{gateMeta}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
