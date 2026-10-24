// Shimmering placeholder blocks shown briefly while a page's data "loads" —
// this app has no backend, so loading is simulated, but the pattern mirrors
// what a real async fetch would show.

export function SkeletonCard() {
  return (
    <div className="skeleton-card">
      <div className="skeleton-row">
        <div className="skeleton-block skeleton-avatar" />
        <div className="skeleton-col">
          <div className="skeleton-block skeleton-line-lg" />
          <div className="skeleton-block skeleton-line-sm" />
        </div>
      </div>
      <div className="skeleton-block skeleton-line-md" />
      <div className="skeleton-block skeleton-line-sm" />
      <div className="skeleton-block skeleton-button" />
    </div>
  );
}

export function SkeletonGrid({ count = 6 }) {
  return (
    <div className="browse-grid">
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}
