// Single brand lockup used everywhere the logo appears — a navy rounded
// badge with "i" in violet and "Find" in white, matching the reference
// wordmark instead of a separate square icon + uppercase text pairing.

export default function Logo({ size = "md" }) {
  return (
    <span className={`logo-badge logo-badge-${size}`}>
      <span className="logo-badge-i">i</span>Find
    </span>
  );
}
