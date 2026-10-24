import { useState, useCallback } from "react";

// Mirrors ifind's hooks/useFilters.ts shape so FilterPanel/BrowseTab logic
// can be ported with the same field names.

const DEFAULT_FILTERS = {
  sortBy: "latest", // "latest" | "deadline" | "stipend"
  sources: [],
  stipendType: "any", // "any" | "paid" | "unpaid" | "performance-based"
  stipendMin: 0,
  stipendMax: 100000,
  workFromHome: false,
  locations: [],
  durationMin: 1,
  durationMax: 12,
  skills: [],
  perks: [],
};

export function useFilters() {
  const [filters, setFilters] = useState(DEFAULT_FILTERS);

  const updateFilter = useCallback((key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  }, []);

  const resetFilters = useCallback(() => {
    setFilters(DEFAULT_FILTERS);
  }, []);

  const toggleLocation = useCallback((loc) => {
    setFilters((prev) => ({
      ...prev,
      locations: prev.locations.includes(loc)
        ? prev.locations.filter((l) => l !== loc)
        : [...prev.locations, loc],
    }));
  }, []);

  const togglePerk = useCallback((perk) => {
    setFilters((prev) => ({
      ...prev,
      perks: prev.perks.includes(perk) ? prev.perks.filter((p) => p !== perk) : [...prev.perks, perk],
    }));
  }, []);

  const addSkill = useCallback((skill) => {
    setFilters((prev) => (prev.skills.includes(skill) ? prev : { ...prev, skills: [...prev.skills, skill] }));
  }, []);

  const removeSkill = useCallback((skill) => {
    setFilters((prev) => ({ ...prev, skills: prev.skills.filter((s) => s !== skill) }));
  }, []);

  return { filters, updateFilter, resetFilters, toggleLocation, togglePerk, addSkill, removeSkill };
}
