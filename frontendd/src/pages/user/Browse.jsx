import { useMemo, useState, useEffect } from "react";
import { InternshipCard } from "../../components/internships/InternshipCard";
import { FilterPanel } from "../../components/internships/FilterPanel";
import { SkeletonGrid } from "../../components/Skeleton";
import { useFilters } from "../../hooks/useFilters";
import { MOCK_INTERNSHIPS, getInternshipId } from "../../data/internships";
import PageHeader from "../../components/PageHeader";

const PAGE_SIZE = 6;

export default function Browse({ section = "02", title = "Browse Internships" }) {
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);
  const [appliedIds, setAppliedIds] = useState(new Set());
  const [savedIds, setSavedIds] = useState(new Set());

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 500);
    return () => clearTimeout(timer);
  }, []);

  const { filters, updateFilter, resetFilters, toggleLocation, togglePerk, addSkill, removeSkill } = useFilters();

  const activeFilterCount = [
    filters.stipendType !== "any",
    filters.locations.length > 0,
    filters.workFromHome,
    filters.durationMin > 1 || filters.durationMax < 12,
    filters.skills.length > 0,
    filters.perks.length > 0,
    filters.sources.length > 0,
  ].filter(Boolean).length;

  const sourceCounts = useMemo(() => {
    const counts = {};
    for (const item of MOCK_INTERNSHIPS) counts[item.source] = (counts[item.source] ?? 0) + 1;
    return counts;
  }, []);

  const results = useMemo(() => {
    let list = [...MOCK_INTERNSHIPS];

    const term = query.trim().toLowerCase();
    if (term) {
      list = list.filter((item) =>
        [item.name, item.company, item.city, ...(item.skills || [])]
          .filter(Boolean)
          .some((val) => String(val).toLowerCase().includes(term))
      );
    }

    if (filters.sources.length > 0) {
      list = list.filter((item) => filters.sources.includes(item.source));
    }

    if (filters.stipendType !== "any") {
      list = list.filter((item) => item.stipend?.type === filters.stipendType);
    }

    if (filters.stipendType === "paid") {
      if (filters.stipendMin > 0) list = list.filter((item) => (item.stipend?.amount || 0) >= filters.stipendMin);
      if (filters.stipendMax < 100000) list = list.filter((item) => (item.stipend?.amount || 0) <= filters.stipendMax);
    }

    if (filters.workFromHome) {
      list = list.filter((item) => item.isRemote);
    }

    if (filters.locations.length > 0) {
      list = list.filter((item) => {
        const itemLocs = [item.city, item.state, item.country, item.isRemote ? "Work from Home" : null]
          .filter(Boolean)
          .map((s) => String(s).toLowerCase());
        return filters.locations.some((loc) => itemLocs.some((il) => il.includes(loc.toLowerCase())));
      });
    }

    list = list.filter((item) => {
      const dur = item.duration?.value || 0;
      if (dur === 0) return true;
      return dur >= filters.durationMin && dur <= filters.durationMax;
    });

    if (filters.skills.length > 0) {
      list = list.filter((item) => {
        const itemSkills = (item.skills || []).map((s) => s.toLowerCase());
        return filters.skills.some((sk) => itemSkills.includes(sk.toLowerCase()));
      });
    }

    if (filters.perks.length > 0) {
      list = list.filter((item) => {
        const itemPerks = (item.perks || []).map((p) => p.toLowerCase());
        return filters.perks.some((pk) => itemPerks.some((ip) => ip.includes(pk.toLowerCase())));
      });
    }

    list.sort((a, b) => {
      if (filters.sortBy === "stipend") return (b.stipend?.amount || 0) - (a.stipend?.amount || 0);
      if (filters.sortBy === "deadline") {
        if (!a.deadlineDate) return 1;
        if (!b.deadlineDate) return -1;
        return new Date(a.deadlineDate).getTime() - new Date(b.deadlineDate).getTime();
      }
      return new Date(b.datePublished).getTime() - new Date(a.datePublished).getTime();
    });

    return list;
  }, [query, filters]);

  useEffect(() => {
    setPage(1);
  }, [query, filters]);

  const totalPages = Math.ceil(results.length / PAGE_SIZE) || 1;
  const startIndex = (page - 1) * PAGE_SIZE;
  const paginated = results.slice(startIndex, startIndex + PAGE_SIZE);

  function handleApply(id) {
    setAppliedIds((prev) => new Set(prev).add(id));
  }

  function handleSave(id) {
    setSavedIds((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }

  return (
    <div className="browse-layout">
      <aside className="browse-filters">
        <FilterPanel
          filters={filters}
          onUpdate={updateFilter}
          onReset={resetFilters}
          onToggleLocation={toggleLocation}
          onTogglePerk={togglePerk}
          onAddSkill={addSkill}
          onRemoveSkill={removeSkill}
          userSkills={["Python", "React", "Node.js"]}
          sourceCounts={sourceCounts}
        />
      </aside>

      <div className="browse-main">
        <PageHeader step={section} title={title} />

        <div className="browse-search">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by role, company or skill…"
          />
        </div>

        <div className="browse-count-row">
          <p>
            {results.length} internships found
            {results.length > 0 && ` (showing ${startIndex + 1}–${Math.min(startIndex + PAGE_SIZE, results.length)})`}
          </p>
          {activeFilterCount > 0 && (
            <button type="button" className="auth-link" onClick={resetFilters}>
              Clear filters ({activeFilterCount})
            </button>
          )}
        </div>

        {loading ? (
          <SkeletonGrid count={6} />
        ) : results.length === 0 ? (
          <div className="card" style={{ textAlign: "center", padding: 48 }}>
            <p style={{ fontWeight: 600, color: "var(--color-navy)" }}>No internships match your criteria.</p>
            <p style={{ fontSize: 13, color: "var(--color-ink-soft)" }}>
              Try broadening your search query or clearing some filters.
            </p>
            <button
              type="button"
              className="btn-secondary"
              onClick={() => {
                resetFilters();
                setQuery("");
              }}
            >
              Reset Search &amp; Filters
            </button>
          </div>
        ) : (
          <div className="browse-grid">
            {paginated.map((internship) => {
              const id = getInternshipId(internship);
              return (
                <InternshipCard
                  key={id}
                  internship={internship}
                  isSaved={savedIds.has(id)}
                  isApplied={appliedIds.has(id)}
                  onSave={handleSave}
                  onApply={handleApply}
                />
              );
            })}
          </div>
        )}

        {!loading && totalPages > 1 && (
          <div className="browse-pagination">
            <button
              type="button"
              className="carousel-arrow"
              disabled={page === 1}
              aria-label="Previous page"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              &lsaquo;
            </button>
            <span className="label">
              Page {page} of {totalPages}
            </span>
            <button
              type="button"
              className="carousel-arrow"
              disabled={page === totalPages}
              aria-label="Next page"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            >
              &rsaquo;
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
