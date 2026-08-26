"""
Shared Internship Formatter
=============================
Converts raw scraper output (from any scraper) into the standardized
MongoDB-compatible JSON format.

Schema (target):
  _id, name, company, applyLink, datePublished, deadlineDate,
  country, state, city, isRemote, stipend{type,amount,currency,period},
  duration{value,unit}, skills[], degree[], field[],
  experienceRequired{min,max,unit}, openings, summary,
  responsibilities[], perks[], tags[], source, isActive, createdAt, updatedAt
"""

import re
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional

# ── City → State mapping (India) ─────────────────────────────────────────────
CITY_STATE_MAP = {
    "mumbai": "Maharashtra", "pune": "Maharashtra", "nagpur": "Maharashtra",
    "nashik": "Maharashtra", "thane": "Maharashtra", "navi mumbai": "Maharashtra",
    "aurangabad": "Maharashtra", "kolhapur": "Maharashtra", "solapur": "Maharashtra",
    "nanded": "Maharashtra", "sangli": "Maharashtra", "jalgaon": "Maharashtra",
    "malegaon": "Maharashtra", "akola": "Maharashtra", "amravati": "Maharashtra",
    "bhiwandi": "Maharashtra", "ulhasnagar": "Maharashtra",
    "delhi": "Delhi", "new delhi": "Delhi",
    "bangalore": "Karnataka", "bengaluru": "Karnataka", "mysore": "Karnataka",
    "mysuru": "Karnataka", "hubli": "Karnataka", "mangalore": "Karnataka",
    "belgaum": "Karnataka", "gulbarga": "Karnataka",
    "chennai": "Tamil Nadu", "coimbatore": "Tamil Nadu", "madurai": "Tamil Nadu",
    "tiruchirappalli": "Tamil Nadu", "salem": "Tamil Nadu", "tiruppur": "Tamil Nadu",
    "erode": "Tamil Nadu", "vellore": "Tamil Nadu", "tirunelveli": "Tamil Nadu",
    "ambattur": "Tamil Nadu",
    "hyderabad": "Telangana", "secunderabad": "Telangana", "warangal": "Telangana",
    "kolkata": "West Bengal", "howrah": "West Bengal", "durgapur": "West Bengal",
    "asansol": "West Bengal", "siliguri": "West Bengal",
    "ahmedabad": "Gujarat", "surat": "Gujarat", "vadodara": "Gujarat",
    "rajkot": "Gujarat", "bhavnagar": "Gujarat", "jamnagar": "Gujarat",
    "jaipur": "Rajasthan", "jodhpur": "Rajasthan", "kota": "Rajasthan",
    "udaipur": "Rajasthan", "ajmer": "Rajasthan", "bikaner": "Rajasthan",
    "lucknow": "Uttar Pradesh", "noida": "Uttar Pradesh", "agra": "Uttar Pradesh",
    "meerut": "Uttar Pradesh", "ghaziabad": "Uttar Pradesh",
    "aligarh": "Uttar Pradesh", "bareilly": "Uttar Pradesh",
    "gorakhpur": "Uttar Pradesh", "saharanpur": "Uttar Pradesh",
    "jhansi": "Uttar Pradesh",
    "gurgaon": "Haryana", "gurugram": "Haryana", "faridabad": "Haryana",
    "chandigarh": "Chandigarh",
    "bhopal": "Madhya Pradesh", "indore": "Madhya Pradesh",
    "jabalpur": "Madhya Pradesh", "ujjain": "Madhya Pradesh",
    "patna": "Bihar", "gaya": "Bihar",
    "ranchi": "Jharkhand", "jamshedpur": "Jharkhand",
    "bhubaneswar": "Odisha", "cuttack": "Odisha", "rourkela": "Odisha",
    "raipur": "Chhattisgarh", "bhilai": "Chhattisgarh",
    "guwahati": "Assam",
    "dehradun": "Uttarakhand",
    "jammu": "Jammu & Kashmir",
    "jalandhar": "Punjab",
    "kochi": "Kerala", "trivandrum": "Kerala",
    "thiruvananthapuram": "Kerala", "kozhikode": "Kerala",
    "calicut": "Kerala", "thrissur": "Kerala",
    "visakhapatnam": "Andhra Pradesh", "guntur": "Andhra Pradesh",
    "nellore": "Andhra Pradesh",
    "pondicherry": "Puducherry", "puducherry": "Puducherry",
}

MONTH_MAP = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6,
    "jul": 7, "july": 7, "aug": 8, "august": 8, "sep": 9, "september": 9,
    "oct": 10, "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}

DEGREE_MAP = {
    r"BE/B\.?Tech|B\.?Tech|B\.?E\.?": "B.Tech",
    r"ME/M\.?Tech|M\.?Tech|M\.?E\.?": "M.Tech",
    r"\bBCA\b": "BCA",
    r"\bMCA\b": "MCA",
    r"\bBSc\b|B\.?Sc": "B.Sc",
    r"\bMSc\b|M\.?Sc": "M.Sc",
    r"\bBBA\b|BBA/BBM": "BBA",
    r"\bMBA\b|MBA/PGDM": "MBA",
    r"\bB\.?Com\b": "B.Com",
    r"\bM\.?Com\b": "M.Com",
    r"\bBA\b": "BA",
    r"\bMA\b": "MA",
    r"\bDiploma\b": "Diploma",
    r"\b12th\s*Pass\b": "12th Pass",
    r"\b10th\s*Pass\b": "10th Pass",
    r"\bPhD\b|Ph\.?D": "PhD",
}

FIELD_MAP = {
    "computer science": "Computer Science",
    "information technology": "Information Technology",
    "computer applications": "Computer Applications",
    "electronics": "Electronics",
    "electrical": "Electrical Engineering",
    "mechanical": "Mechanical Engineering",
    "civil": "Civil Engineering",
    "commerce": "Commerce",
    "management": "Management",
    "marketing": "Marketing",
    "finance": "Finance",
    "design": "Design",
    "arts": "Arts",
    "science": "Science",
    "engineering": "Engineering",
}

# Common perks mentioned in internship descriptions
PERK_PATTERNS = [
    (r"\bcertificate\b", "Certificate"),
    (r"\bletter of recommendation\b|\blor\b", "Letter of Recommendation"),
    (r"\bflexible hours?\b|\bflexible timing\b", "Flexible hours"),
    (r"\b5\s*days?/?\s*week\b|\bfive days?\s*a\s*week\b", "5 days/week"),
    (r"\bwork from home\b|\bwfh\b|\bremote\b", "Work from home"),
    (r"\bfree\s*(?:lunch|food|meals?)\b|\bfood\s*provided\b", "Free meals"),
    (r"\bstipend\b", "Stipend"),
    (r"\bpre-placement\s*offer\b|\bppo\b", "Pre-Placement Offer"),
    (r"\bmentorship\b|\bmentor\b", "Mentorship"),
    (r"\bhealth\s*insurance\b|\bmedical\s*insurance\b", "Health Insurance"),
    (r"\bcasual\s*dress\b|\binformal\s*dress\b", "Informal dress code"),
    (r"\bfree\s*snacks?\b|\bsnacks?\s*provided\b", "Free snacks"),
    (r"\bperformance\s*bonus\b|\bincentive\b", "Performance bonus"),
    (r"\bstock\s*options?\b|\besop\b", "Stock options"),
]


# ============================================================================
#  HELPERS
# ============================================================================
def _generate_oid(source: str, title: str, company: str, link: str) -> str:
    raw = f"{source}:{title}:{company}:{link}"
    return hashlib.sha256(raw.encode()).hexdigest()[:24]


def _parse_date(raw: str) -> Optional[datetime]:
    if not raw or raw in ("N/A", ""):
        return None
    cleaned = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", raw.strip())
    cleaned = re.sub(r"'(\d{2})\b", r" 20\1", cleaned)
    formats = [
        "%d %b %Y", "%d %B %Y", "%b %d %Y", "%B %d %Y",
        "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y",
        "%d %b, %Y", "%b %d, %Y", "%B %d, %Y",
        "%d %b %y", "%b %d %y",
        "%A, %B %d, %Y", "%A, %B %d %Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    parts = cleaned.split()
    if len(parts) >= 2:
        try:
            day = int(re.search(r"\d+", parts[0]).group())
            mon = MONTH_MAP.get(parts[1].lower()[:3])
            if mon:
                year = datetime.now().year
                d = datetime(year, mon, day)
                if d < datetime.now() - timedelta(days=30):
                    d = datetime(year + 1, mon, day)
                return d
        except Exception:
            pass
    return None


def _parse_relative_date(raw: str) -> Optional[datetime]:
    if not raw or raw in ("N/A", ""):
        return None
    now = datetime.now()
    lower = raw.lower().strip()
    if lower in ("today", "just now"):
        return now
    if lower == "yesterday":
        return now - timedelta(days=1)
    m = re.search(r"(\d+)\s*(day|hour|week|month|year)s?\s*ago", lower)
    if m:
        n, unit = int(m.group(1)), m.group(2)
        delta = {
            "hour": timedelta(hours=n),
            "day": timedelta(days=n),
            "week": timedelta(weeks=n),
            "month": timedelta(days=n * 30),
            "year": timedelta(days=n * 365),
        }.get(unit)
        if delta:
            return now - delta
    return None


def _to_mongo_date(dt: Optional[datetime]) -> Optional[dict]:
    if not dt:
        return None
    return {"$date": dt.strftime("%Y-%m-%dT00:00:00.000Z")}


def _parse_stipend(raw: str) -> dict:
    """Parse stipend string into {type, amount, currency, period}."""
    result = {"type": "unpaid", "amount": 0, "currency": "INR", "period": "monthly"}

    if not raw or raw in ("N/A", ""):
        return result

    lower = raw.lower()

    if "unpaid" in lower:
        result["type"] = "unpaid"
        return result

    if "not disclosed" in lower:
        result["type"] = "not_disclosed"
        return result

    if "performance" in lower:
        result["type"] = "performance_based"
        return result

    # Extract all numeric values
    amounts = re.findall(r"[\d,]+", raw)
    nums = [int(a.replace(",", "")) for a in amounts if a.replace(",", "").isdigit() and int(a.replace(",", "")) > 0]

    if nums:
        result["type"] = "paid"
        result["amount"] = max(nums)

    # Detect period
    if re.search(r"lpa|l\.?p\.?a|lacs?|lakhs?", lower):
        result["period"] = "yearly"
        if result["amount"] < 1000:          # stored as e.g. 3.5 LPA
            result["amount"] = int(result["amount"] * 100000)
    elif "lump" in lower:
        result["period"] = "lump_sum"
    elif any(k in lower for k in ["/month", "per month", "monthly", "/mo", "pm", "p.m."]):
        result["period"] = "monthly"
    else:
        result["period"] = "monthly"        # default for internships

    return result


def _parse_duration(raw: str) -> dict:
    """Parse duration string into {value, unit}."""
    result = {"value": 0, "unit": "months"}
    if not raw or raw in ("N/A", ""):
        return result
    lower = raw.lower()
    m = re.search(r"(\d+)\s*(?:[-–]\s*(\d+))?\s*(months?|weeks?|years?|yrs?)", lower)
    if m:
        lo = int(m.group(1))
        hi = int(m.group(2)) if m.group(2) else lo
        unit_raw = m.group(3)
        result["value"] = hi
        if "week" in unit_raw:
            result["unit"] = "weeks"
        elif "year" in unit_raw or "yr" in unit_raw:
            result["unit"] = "years"
        else:
            result["unit"] = "months"
    return result


def _parse_location(raw: str) -> dict:
    """Parse location string into {country, state, city, isRemote}."""
    result = {"country": "India", "state": "", "city": "", "isRemote": False}
    if not raw or raw in ("N/A", ""):
        return result

    lower = raw.lower()
    remote_keywords = ["work from home", "remote", "wfh", "online", "virtual"]
    if any(k in lower for k in remote_keywords):
        result["isRemote"] = True

    parts = re.split(r"[,/|]", raw)
    for part in parts:
        part_clean = part.strip()
        part_lower = part_clean.lower().strip()
        if any(k in part_lower for k in remote_keywords):
            continue
        if part_lower in CITY_STATE_MAP:
            result["city"] = part_clean.title()
            result["state"] = CITY_STATE_MAP[part_lower]
            break
        for city_key, state_val in CITY_STATE_MAP.items():
            if city_key in part_lower and len(city_key) > 3:
                result["city"] = city_key.title()
                result["state"] = state_val
                break
        if result["city"]:
            break

    return result


def _infer_degrees(text: str) -> list:
    degrees = []
    for pattern, degree_name in DEGREE_MAP.items():
        if re.search(pattern, text, re.IGNORECASE) and degree_name not in degrees:
            degrees.append(degree_name)
    return degrees


def _infer_fields(text: str) -> list:
    fields = []
    lower = text.lower()
    for keyword, field_name in FIELD_MAP.items():
        if keyword in lower and field_name not in fields:
            fields.append(field_name)
    return fields


def _extract_responsibilities(description: str) -> list:
    """
    Extract bullet-point responsibilities from a description string.
    Looks for numbered lists, dash/bullet lists, or sentences starting
    with action verbs.
    """
    if not description or description == "N/A":
        return []

    responsibilities = []

    # Strategy 1: numbered list  "1. Do X  2. Do Y"
    numbered = re.findall(
        r"(?:^|\n)\s*\d+[\.\)]\s*(.+?)(?=\n\s*\d+[\.\)]|\Z)",
        description, re.DOTALL
    )
    if numbered:
        for item in numbered:
            item = re.sub(r"\s+", " ", item).strip()
            if 10 < len(item) < 300:
                responsibilities.append(item)
        if responsibilities:
            return responsibilities[:10]

    # Strategy 2: dash / bullet list  "- Do X\n- Do Y"
    bulleted = re.findall(
        r"(?:^|\n)\s*[-•*]\s*(.+?)(?=\n\s*[-•*]|\Z)",
        description, re.DOTALL
    )
    if bulleted:
        for item in bulleted:
            item = re.sub(r"\s+", " ", item).strip()
            if 10 < len(item) < 300:
                responsibilities.append(item)
        if responsibilities:
            return responsibilities[:10]

    # Strategy 3: split on sentence boundaries, keep action-verb sentences
    ACTION_VERBS = (
        r"^(develop|build|design|implement|create|write|manage|support|assist|"
        r"work|collaborate|analyze|analyse|research|test|maintain|coordinate|"
        r"prepare|handle|conduct|perform|ensure|review|monitor|track|report|"
        r"identify|generate|execute|deliver|contribute|help|learn|participate)"
    )
    sentences = re.split(r"(?<=[.!?])\s+", description)
    for s in sentences:
        s = s.strip()
        if re.match(ACTION_VERBS, s, re.IGNORECASE) and 15 < len(s) < 250:
            responsibilities.append(s)
    return responsibilities[:8]


def _extract_perks(text: str) -> list:
    """Extract perks/benefits mentioned in the text."""
    if not text or text == "N/A":
        return []
    perks = []
    lower = text.lower()
    for pattern, perk_name in PERK_PATTERNS:
        if re.search(pattern, lower) and perk_name not in perks:
            perks.append(perk_name)
    return perks


def _extract_openings(text: str) -> int:
    """Try to extract number of openings from text."""
    if not text or text == "N/A":
        return 1
    m = re.search(
        r"(\d+)\s*(?:opening|position|seat|vacanc|slot)s?",
        text, re.IGNORECASE
    )
    if m:
        n = int(m.group(1))
        return n if 1 <= n <= 500 else 1
    return 1


def _generate_summary(title: str, company: str, description: str) -> str:
    """Generate a concise summary."""
    if description and description != "N/A" and len(description) > 30:
        if len(description) > 300:
            end = description[:300].rfind(".")
            if end > 80:
                return description[:end + 1]
            return description[:300] + "..."
        return description
    return f"{title} opportunity at {company}."


def _generate_tags(title: str, role: str, skills: list, is_remote: bool) -> list:
    tags = set()
    for word in (role or "").lower().split():
        word = word.strip("/ ")
        if word and len(word) > 1:
            tags.add(word)
    for skill in skills[:5]:
        tags.add(skill.lower())
    title_lower = title.lower()
    for kw in ["intern", "internship", "trainee", "apprentice", "fresher"]:
        if kw in title_lower:
            tags.add(kw)
            break
    if is_remote:
        tags.add("remote")
    tags.discard("")
    tags.discard("n/a")
    tags.discard("other")
    return sorted(list(tags))[:10]


# ============================================================================
#  MAIN FORMATTER
# ============================================================================
def format_internship(raw: dict, source: str) -> dict:
    """
    Convert a raw scraper dict into the standardized MongoDB format.

    Handles all five scrapers:
      internshala, naukri, unstop, freshersworld, letsintern
    """
    # ── Normalize field names across scrapers ─────────────────────────────
    title        = raw.get("title", raw.get("name", "N/A")) or "N/A"
    company      = raw.get("company", "N/A") or "N/A"
    link         = raw.get("link", raw.get("applyLink", "N/A")) or "N/A"
    location_raw = raw.get("location", "N/A") or "N/A"
    stipend_raw  = raw.get("stipend", raw.get("salary", "N/A")) or "N/A"
    duration_raw = raw.get("duration", raw.get("experience", "N/A")) or "N/A"
    skills_raw   = raw.get("skills", []) or []
    role         = raw.get("type", "Other") or "Other"
    description  = raw.get("description", "N/A") or "N/A"

    apply_by_raw = raw.get("apply_by", raw.get("deadline", "N/A")) or "N/A"
    posted_raw   = raw.get("posted", raw.get("start_date", "")) or ""

    quals_raw    = raw.get("qualifications", "") or ""
    full_text    = f"{title} {description} {quals_raw} {' '.join(skills_raw)}"

    # ── ObjectId ──────────────────────────────────────────────────────────
    oid = _generate_oid(source, title, company, link)

    # ── Dates ─────────────────────────────────────────────────────────────
    date_published = None
    if posted_raw and posted_raw != "N/A":
        date_published = _parse_date(posted_raw) or _parse_relative_date(posted_raw)
    if not date_published:
        date_published = datetime.now()

    deadline_date = None
    if apply_by_raw and apply_by_raw != "N/A":
        deadline_date = _parse_date(apply_by_raw)
        if not deadline_date:
            remain = re.search(r"(\d+)\s*days?\s*(?:left|remaining)?", apply_by_raw, re.IGNORECASE)
            if remain:
                deadline_date = datetime.now() + timedelta(days=int(remain.group(1)))

    # ── Location ──────────────────────────────────────────────────────────
    loc = _parse_location(location_raw)

    # ── Stipend ───────────────────────────────────────────────────────────
    stipend = _parse_stipend(stipend_raw)

    # ── Duration ──────────────────────────────────────────────────────────
    duration = _parse_duration(duration_raw)

    # ── Degrees & Fields ──────────────────────────────────────────────────
    degrees = _infer_degrees(full_text)
    fields  = _infer_fields(full_text)

    # ── Experience required ───────────────────────────────────────────────
    exp = {"min": 0, "max": 0, "unit": "months"}
    exp_raw = raw.get("experience", raw.get("duration", "")) or ""
    if exp_raw:
        em = re.search(
            r"(\d+)\s*[-–]\s*(\d+)\s*(months?|years?|yrs?)",
            str(exp_raw), re.IGNORECASE
        )
        if em:
            exp["min"] = int(em.group(1))
            exp["max"] = int(em.group(2))
            u = em.group(3).lower()
            exp["unit"] = "years" if ("yr" in u or "year" in u) else "months"
        elif re.search(r"fresher|0\s*year|entry", str(exp_raw), re.IGNORECASE):
            exp = {"min": 0, "max": 0, "unit": "months"}

    # ── Responsibilities ──────────────────────────────────────────────────
    # Prefer explicit field from scraper, else extract from description
    responsibilities = raw.get("responsibilities", []) or []
    if not responsibilities:
        responsibilities = _extract_responsibilities(description)

    # ── Perks ─────────────────────────────────────────────────────────────
    perks = raw.get("perks", []) or []
    if not perks:
        perks = _extract_perks(f"{description} {full_text}")

    # ── Openings ──────────────────────────────────────────────────────────
    openings = raw.get("openings", 0)
    if not openings or openings == 0:
        openings = _extract_openings(f"{title} {description}")

    # ── Summary ───────────────────────────────────────────────────────────
    summary = raw.get("summary", "") or ""
    if not summary or summary == "N/A":
        summary = _generate_summary(title, company, description)

    # ── Tags ──────────────────────────────────────────────────────────────
    tags = _generate_tags(title, role, skills_raw, loc["isRemote"])

    # ── Build output ──────────────────────────────────────────────────────
    now_date = _to_mongo_date(datetime.now())

    return {
        "_id":              {"$oid": oid},
        "name":             title,
        "company":          company,
        "applyLink":        link,
        "datePublished":    _to_mongo_date(date_published),
        "deadlineDate":     _to_mongo_date(deadline_date),
        "country":          loc["country"],
        "state":            loc["state"],
        "city":             loc["city"],
        "isRemote":         loc["isRemote"],
        "stipend":          stipend,
        "duration":         duration,
        "skills":           skills_raw,
        "degree":           degrees,
        "field":            fields,
        "experienceRequired": exp,
        "openings":         openings,
        "summary":          summary,
        "responsibilities": responsibilities,
        "perks":            perks,
        "tags":             tags,
        "source":           source,
        "isActive":         True,
        "createdAt":        now_date,
        "updatedAt":        now_date,
    }


# ============================================================================
#  BATCH FORMAT + SAVE
# ============================================================================
def format_and_save(
    raw_items: list,
    source: str,
    output_path: str,
    raw_output_path: Optional[str] = None,
) -> list:
    if raw_output_path:
        with open(raw_output_path, "w", encoding="utf-8") as f:
            json.dump(raw_items, f, indent=2, ensure_ascii=False)

    formatted = []
    for item in raw_items:
        try:
            formatted.append(format_internship(item, source))
        except Exception as e:
            print(f"[WARN] Could not format item: {e}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(formatted, f, indent=2, ensure_ascii=False)

    print(f"Formatted {len(formatted)} internships -> {output_path}")
    return formatted


# ============================================================================
#  CLI
# ============================================================================
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python format_internship.py <input.json> <source> [output.json]")
        print("  source: internshala | naukri | unstop | freshersworld | letsintern")
        sys.exit(1)

    input_path  = sys.argv[1]
    source      = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else input_path.replace(".json", "_formatted.json")

    with open(input_path, "r", encoding="utf-8") as f:
        raw_items = json.load(f)

    result = format_and_save(raw_items, source, output_path)
    print(f"Done. {len(result)} items formatted from '{source}'.")
