// Shared rotation of accent colors for small decorative chips — company
// initials, internship logos, category icons — so a list of items reads as
// visually varied instead of everything being flat navy/violet. Deterministic
// by seed (e.g. a name) so the same item always gets the same color.

export const ACCENT_COLORS = [
  "var(--color-accent-indigo)",
  "var(--color-tag-purple)",
  "var(--color-tag-green)",
  "var(--color-accent-rose)",
  "var(--color-accent-sky)",
  "var(--color-accent-amber2)",
  "var(--color-accent-teal)",
  "var(--color-accent-coral)",
  "var(--color-accent-lime)",
  "var(--color-accent-fuchsia)",
];

export function accentColor(seed) {
  const str = String(seed ?? "");
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = (hash * 31 + str.charCodeAt(i)) % 1000003;
  }
  return ACCENT_COLORS[Math.abs(hash) % ACCENT_COLORS.length];
}
