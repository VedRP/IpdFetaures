"""
Finalize Freshersworld scrape results.
=======================================
Pipeline:
  1. Load fw_raw.json
  2. Deduplicate by job ID
  3. AI-enrich missing fields (Groq free tier → Gemini fallback)
  4. Format to standard MongoDB schema via format_internship.py
  5. Save fw_internships.json

Run from workspace root:
    python freshersworld_scraper/finalize.py

Requires (free, no credit card):
    GROQ_API_KEY   → https://console.groq.com
    GEMINI_API_KEY → https://aistudio.google.com  (optional fallback)

    pip install groq google-generativeai python-dotenv
"""

import json
import sys
import os
import logging
from collections import Counter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("finalize")

# Allow running from workspace root or from freshersworld_scraper/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from format_internship import format_and_save
from freshersworld_scraper.ai_enricher import enrich_batch, GROQ_API_KEY, GEMINI_API_KEY

RAW_PATH      = "freshersworld_scraper/fw_raw.json"
ENRICHED_PATH = "freshersworld_scraper/fw_enriched.json"   # intermediate
FINAL_PATH    = "freshersworld_scraper/fw_internships.json"


def main():
    # ── 1. Load raw ───────────────────────────────────────────────────────────
    log.info("Loading %s ...", RAW_PATH)
    with open(RAW_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    log.info("Loaded %d raw items", len(raw))

    # ── 2. Deduplicate by job ID ──────────────────────────────────────────────
    seen, unique = set(), []
    for item in raw:
        key = item.get("id") or item.get("link", "")
        if key and key not in seen:
            seen.add(key)
            unique.append(item)
    log.info("After dedup: %d unique items", len(unique))

    # ── 3. AI enrichment ──────────────────────────────────────────────────────
    if not GROQ_API_KEY and not GEMINI_API_KEY:
        log.warning(
            "\n" + "="*60 + "\n"
            "No AI API key found — skipping enrichment.\n"
            "Fields like skills, summary, responsibilities will be empty.\n\n"
            "To enable (FREE, no credit card):\n"
            "  1. Get Groq key at https://console.groq.com\n"
            "  2. set GROQ_API_KEY=gsk_your_key_here\n"
            "  3. pip install groq\n"
            "  4. Re-run this script.\n"
            + "="*60
        )
        enriched = unique
    else:
        provider = "Groq" if GROQ_API_KEY else "Gemini"
        log.info("Starting AI enrichment with %s (%d items)...", provider, len(unique))

        # Count how many actually need enrichment
        needs = sum(
            1 for i in unique
            if not i.get("skills") or not i.get("summary") or not i.get("responsibilities")
        )
        log.info("%d/%d items need enrichment", needs, len(unique))

        enriched = enrich_batch(unique)

        # Save intermediate enriched raw (useful for debugging)
        with open(ENRICHED_PATH, "w", encoding="utf-8") as f:
            json.dump(enriched, f, indent=2, ensure_ascii=False)
        log.info("Saved enriched raw → %s", ENRICHED_PATH)

    # ── 4. Format to standard schema ─────────────────────────────────────────
    log.info("Formatting to standard MongoDB schema...")
    formatted = format_and_save(
        enriched,
        source="freshersworld",
        output_path=FINAL_PATH,
    )

    # ── 5. Quality report ─────────────────────────────────────────────────────
    total = len(formatted)
    print(f"\n{'='*50}")
    print(f"Total internships: {total}")
    print(f"{'='*50}")

    print("\n=== DATA COMPLETENESS ===")
    check_fields = [
        ("skills",           lambda i: bool(i.get("skills"))),
        ("degree",           lambda i: bool(i.get("degree"))),
        ("field",            lambda i: bool(i.get("field"))),
        ("summary",          lambda i: bool(i.get("summary")) and "opportunity at" not in i.get("summary","")),
        ("responsibilities", lambda i: bool(i.get("responsibilities"))),
        ("perks",            lambda i: bool(i.get("perks"))),
        ("duration",         lambda i: i.get("duration", {}).get("value", 0) > 0),
        ("stipend (paid)",   lambda i: i.get("stipend", {}).get("type") == "paid"),
        ("city",             lambda i: bool(i.get("city"))),
        ("isRemote",         lambda i: i.get("isRemote") is True),
    ]
    for label, check in check_fields:
        count = sum(1 for i in formatted if check(i))
        pct = count * 100 // total if total else 0
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
        print(f"  {label:<20} {bar} {pct:3d}%  ({count}/{total})")

    print("\n=== ROLE DISTRIBUTION ===")
    for role, cnt in Counter(i.get("tags", ["other"])[0] if i.get("tags") else "other"
                             for i in formatted).most_common(8):
        print(f"  {role:<30} {cnt}")

    print(f"\nSaved → {FINAL_PATH}")


if __name__ == "__main__":
    main()
