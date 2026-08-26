"""
AI Enricher for Freshersworld Internships
==========================================
Sends ALL items in ONE API call — no per-item loop.

Primary  : Groq  — llama-3.1-8b-instant  (14,400 req/day free)
Fallback : Gemini — gemini-1.5-flash      (1,500 req/day free)

Setup (free, no credit card):
  Groq   → https://console.groq.com       → API Keys → Create key
  Gemini → https://aistudio.google.com    → Get API key

  Put in .env at workspace root:
    GROQ_API_KEY=gsk_...
    GEMINI_API_KEY=AIza...  (optional)

Install:
    pip install groq google-generativeai python-dotenv
"""

import os
import re
import json
import time
import logging
from typing import Optional

log = logging.getLogger("ai_enricher")

# ── Load .env ─────────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    _env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    load_dotenv(dotenv_path=os.path.abspath(_env_path), override=True)
except ImportError:
    pass

GROQ_API_KEY   = os.environ.get("GROQ_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Groq token limit per request — llama-3.1-8b-instant allows 6000 TPM
# Each item summary is ~80 tokens input + ~150 tokens output
# Safe chunk size: 20 items per call (fits well within limits)
CHUNK_SIZE = 20

# ── Clients (lazy init) ───────────────────────────────────────────────────────
_groq_client  = None
_gemini_model = None

def _get_groq():
    global _groq_client
    if _groq_client is None and GROQ_API_KEY:
        try:
            from groq import Groq
            _groq_client = Groq(api_key=GROQ_API_KEY)
            log.info("Groq client ready")
        except ImportError:
            log.warning("groq not installed — run: pip install groq")
    return _groq_client

def _get_gemini():
    global _gemini_model
    if _gemini_model is None and GEMINI_API_KEY:
        try:
            from google import genai
            _gemini_model = genai.Client(api_key=GEMINI_API_KEY)
            log.info("Gemini client ready")
        except ImportError:
            log.warning("google-genai not installed — run: pip install google-genai")
    return _gemini_model


# ============================================================================
#  BUILD ONE PROMPT FOR A CHUNK OF ITEMS
# ============================================================================
def _build_batch_prompt(items: list) -> str:
    """
    Build a single prompt that asks the LLM to enrich ALL items at once.
    Returns a prompt that expects a JSON array response.
    """
    lines = []
    for i, item in enumerate(items):
        title  = item.get("title", "N/A")
        company= item.get("company", "N/A")
        loc    = item.get("location", "N/A")
        salary = item.get("salary", "N/A")
        exp    = item.get("experience", "N/A")
        quals  = item.get("qualifications", "N/A")
        role   = item.get("type", "N/A")
        skills = ", ".join(item.get("skills", [])) or "unknown"
        lines.append(
            f'  {{"index":{i},"title":"{title}","company":"{company}",'
            f'"location":"{loc}","salary":"{salary}","experience":"{exp}",'
            f'"role":"{role}","skills":"{skills}","qualifications":"{quals}"}}'
        )

    items_json = "[\n" + ",\n".join(lines) + "\n]"

    return f"""You are a data enrichment assistant for an internship job board.
Below is a JSON array of {len(items)} internship records with partial data.
Return a JSON array of the same length where each element has EXACTLY these fields:

{{
  "index": <same index as input>,
  "skills": ["Skill1", "Skill2"],
  "degree": ["B.Tech", "BCA"],
  "field": ["Computer Science", "Information Technology"],
  "summary": "2-3 sentence description of the role.",
  "responsibilities": ["Do X", "Do Y", "Do Z"],
  "perks": ["Certificate", "Mentorship"],
  "duration_months": 3,
  "openings": 1
}}

Rules:
- Return ONLY a valid JSON array. No markdown, no explanation, no extra text.
- If a field cannot be inferred, use [] for arrays, "" for strings, 0 for numbers.
- Skills: capitalize each (e.g. "Python", "React", "MS Excel").
- Degree options: B.Tech, B.E., BCA, BBA, B.Sc, B.Com, MBA, MCA, M.Tech, Diploma, Any Graduate.
- Field options: Computer Science, Information Technology, Electronics, Mechanical Engineering,
  Civil Engineering, Commerce, Management, Marketing, Finance, Design, Arts, Science, Engineering.
- responsibilities: 3-5 action-verb sentences specific to the role.
- perks: only include if clearly applicable (Certificate, Mentorship, Flexible hours,
  Work from home, Pre-Placement Offer, Performance bonus, Letter of Recommendation).

Input data:
{items_json}
"""


# ============================================================================
#  CALL LLM  (Groq → Gemini fallback)
# ============================================================================
def _call_llm(prompt: str, retries: int = 3) -> Optional[str]:
    """Single LLM call — Groq first, Gemini as fallback."""

    groq = _get_groq()
    if groq:
        for attempt in range(1, retries + 1):
            try:
                resp = groq.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=4000,   # enough for 20 items
                )
                return resp.choices[0].message.content.strip()
            except Exception as e:
                err = str(e)
                if "429" in err or "rate_limit" in err.lower():
                    wait = 30 * attempt
                    log.warning("Groq rate limit — waiting %ds (attempt %d/%d)", wait, attempt, retries)
                    time.sleep(wait)
                else:
                    log.warning("Groq error attempt %d: %s", attempt, e)
                    time.sleep(3)

    gemini = _get_gemini()
    if gemini:
        for attempt in range(1, retries + 1):
            try:
                from google import genai as genai_mod
                resp = gemini.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                )
                return resp.text.strip()
            except Exception as e:
                err = str(e)
                if "429" in err or "quota" in err.lower():
                    wait = 30 * attempt
                    log.warning("Gemini rate limit — waiting %ds", wait)
                    time.sleep(wait)
                else:
                    log.warning("Gemini error attempt %d: %s", attempt, e)
                    time.sleep(3)

    log.error("Both Groq and Gemini failed — check your API keys in .env")
    return None


# ============================================================================
#  PARSE LLM RESPONSE  →  list of enrichment dicts
# ============================================================================
def _parse_batch_response(raw_text: str, expected_count: int) -> list:
    """
    Extract the JSON array from the LLM response.
    Returns a list of dicts (one per item), or empty list on failure.
    """
    if not raw_text:
        return []

    # Strip markdown fences
    text = re.sub(r"```(?:json)?\s*", "", raw_text).strip().rstrip("`").strip()

    # Find the outermost [ ... ] array
    m = re.search(r"\[.*\]", text, re.DOTALL)
    if not m:
        # Maybe the model returned a single object — wrap it
        m2 = re.search(r"\{.*\}", text, re.DOTALL)
        if m2:
            text = "[" + m2.group(0) + "]"
        else:
            log.warning("No JSON array found in LLM response")
            return []
    else:
        text = m.group(0)

    # Fix trailing commas
    text = re.sub(r",\s*([}\]])", r"\1", text)

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            parsed = [parsed]
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError as e:
        log.warning("JSON parse error: %s", e)
        return []


# ============================================================================
#  MERGE enrichment into original item
# ============================================================================
def _merge(original: dict, enriched: dict) -> dict:
    """Merge AI-generated fields into original — never overwrite existing data."""
    result = dict(original)

    if not result.get("skills") and enriched.get("skills"):
        result["skills"] = [s for s in enriched["skills"] if isinstance(s, str)][:10]

    if not result.get("degree") and enriched.get("degree"):
        result["degree"] = [d for d in enriched["degree"] if isinstance(d, str)]

    if not result.get("field") and enriched.get("field"):
        result["field"] = [f for f in enriched["field"] if isinstance(f, str)]

    if not result.get("summary") and enriched.get("summary"):
        result["summary"] = str(enriched["summary"])[:400]

    if not result.get("responsibilities") and enriched.get("responsibilities"):
        result["responsibilities"] = [
            r for r in enriched["responsibilities"] if isinstance(r, str)
        ][:6]

    if not result.get("perks") and enriched.get("perks"):
        result["perks"] = [p for p in enriched["perks"] if isinstance(p, str)]

    # Duration: fill only if currently 0
    dur = result.get("duration", {})
    if isinstance(dur, dict) and dur.get("value", 0) == 0:
        dm = enriched.get("duration_months", 0)
        if isinstance(dm, (int, float)) and int(dm) > 0:
            result["duration"] = {"value": int(dm), "unit": "months"}

    # Openings: fill only if still default 1
    if result.get("openings", 1) == 1:
        op = enriched.get("openings", 1)
        if isinstance(op, (int, float)) and int(op) > 1:
            result["openings"] = int(op)

    return result


# ============================================================================
#  PUBLIC API
# ============================================================================
def enrich_batch(items: list) -> list:
    """
    Enrich a list of raw freshersworld items using ONE API call per chunk.

    Items that already have all fields are passed through unchanged.
    Items missing fields are sent to the LLM in batches of CHUNK_SIZE.

    Args:
        items: list of raw dicts from freshersworld scraper

    Returns:
        list of enriched dicts (same order, same length)
    """
    if not GROQ_API_KEY and not GEMINI_API_KEY:
        log.error(
            "No API key found. Set GROQ_API_KEY in .env\n"
            "  Free key at: https://console.groq.com"
        )
        return items

    # Split into: items that need enrichment vs already complete
    needs_idx  = []   # indices into `items` that need enrichment
    for i, item in enumerate(items):
        if (not item.get("skills")
                or not item.get("summary")
                or not item.get("responsibilities")
                or not item.get("degree")
                or not item.get("field")):
            needs_idx.append(i)

    if not needs_idx:
        log.info("All %d items already complete — no enrichment needed", len(items))
        return items

    log.info("%d/%d items need enrichment — sending in chunks of %d",
             len(needs_idx), len(items), CHUNK_SIZE)

    # Work on a copy
    results = list(items)

    # Process in chunks — each chunk = ONE API call
    for chunk_start in range(0, len(needs_idx), CHUNK_SIZE):
        chunk_indices = needs_idx[chunk_start: chunk_start + CHUNK_SIZE]
        chunk_items   = [items[i] for i in chunk_indices]
        chunk_num     = chunk_start // CHUNK_SIZE + 1
        total_chunks  = (len(needs_idx) + CHUNK_SIZE - 1) // CHUNK_SIZE

        log.info("  Chunk %d/%d — %d items → 1 API call",
                 chunk_num, total_chunks, len(chunk_items))

        prompt   = _build_batch_prompt(chunk_items)
        raw_resp = _call_llm(prompt)

        if not raw_resp:
            log.warning("  Chunk %d failed — keeping originals", chunk_num)
            continue

        enriched_list = _parse_batch_response(raw_resp, len(chunk_items))

        if not enriched_list:
            log.warning("  Chunk %d — could not parse response, keeping originals", chunk_num)
            continue

        # Map by index field back to original positions
        enriched_by_idx = {e.get("index", i): e for i, e in enumerate(enriched_list)}

        filled = 0
        for local_i, orig_idx in enumerate(chunk_indices):
            enrichment = enriched_by_idx.get(local_i, {})
            if enrichment:
                results[orig_idx] = _merge(items[orig_idx], enrichment)
                filled += 1

        log.info("  Chunk %d/%d done — %d/%d items enriched",
                 chunk_num, total_chunks, filled, len(chunk_items))

        # Small pause between chunks only (not between items)
        if chunk_start + CHUNK_SIZE < len(needs_idx):
            time.sleep(1)

    return results


# ============================================================================
#  CLI
# ============================================================================
if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    input_path  = sys.argv[1] if len(sys.argv) > 1 else "freshersworld_scraper/fw_raw.json"
    output_path = sys.argv[2] if len(sys.argv) > 2 else input_path.replace(".json", "_enriched.json")

    if not GROQ_API_KEY and not GEMINI_API_KEY:
        print("ERROR: No API key. Set GROQ_API_KEY in .env")
        print("Free key at: https://console.groq.com")
        sys.exit(1)

    with open(input_path, encoding="utf-8") as f:
        raw_items = json.load(f)

    log.info("Enriching %d items...", len(raw_items))
    enriched = enrich_batch(raw_items)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)

    log.info("Saved → %s", output_path)

    total = len(enriched)
    print("\n=== ENRICHMENT RESULTS ===")
    for field in ["skills", "degree", "field", "summary", "responsibilities", "perks"]:
        filled = sum(1 for i in enriched if i.get(field) and i[field] != "N/A")
        pct = filled * 100 // total if total else 0
        print(f"  {field:<18} {filled}/{total} ({pct}%)")
