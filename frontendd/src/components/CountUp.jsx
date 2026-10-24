import { useEffect, useRef, useState } from "react";

// Animates a displayed stat (e.g. "50,000+", "2M+", "95%") counting up from 0
// to its final value once it scrolls into view. Parses the leading numeric
// portion and preserves whatever suffix/formatting follows it (commas, "+",
// "%", "M", ...) so no new data is needed — purely a visual effect.

function parseStat(value) {
  const match = String(value).match(/^([\d,]+)(.*)$/);
  if (!match) return { target: 0, suffix: String(value), hasCommas: false };
  const digits = match[1];
  return {
    target: parseInt(digits.replace(/,/g, ""), 10),
    suffix: match[2],
    hasCommas: digits.includes(","),
  };
}

export default function CountUp({ value, duration = 1200 }) {
  const { target, suffix, hasCommas } = parseStat(value);
  const [display, setDisplay] = useState(0);
  const ref = useRef(null);
  const hasRun = useRef(false);

  useEffect(() => {
    if (!ref.current || Number.isNaN(target)) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasRun.current) {
          hasRun.current = true;
          const start = performance.now();

          function tick(now) {
            const elapsed = now - start;
            const progress = Math.min(1, elapsed / duration);
            const eased = 1 - Math.pow(1 - progress, 3);
            setDisplay(Math.round(target * eased));
            if (progress < 1) requestAnimationFrame(tick);
          }
          requestAnimationFrame(tick);
          observer.disconnect();
        }
      },
      { threshold: 0.4 }
    );

    observer.observe(ref.current);
    return () => observer.disconnect();
  }, [target, duration]);

  if (Number.isNaN(target)) {
    return <span ref={ref}>{value}</span>;
  }

  const formatted = hasCommas ? display.toLocaleString("en-IN") : String(display);

  return (
    <span ref={ref}>
      {formatted}
      {suffix}
    </span>
  );
}
