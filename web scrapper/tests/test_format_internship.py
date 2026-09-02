"""
test_format_internship.py
--------------------------
Unit test suite for web scrapper/format_internship.py.
Tests date parsing, relative dates, stipend conversions (LPA, monthly, weekly, lump sum),
location mapping, degrees, skills, and full internship formatting.
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add web scrapper to sys.path
scraper_dir = Path(__file__).resolve().parent.parent
if str(scraper_dir) not in sys.path:
    sys.path.insert(0, str(scraper_dir))

from format_internship import (
    format_internship,
    _parse_date,
    _parse_relative_date,
    _parse_stipend,
    _parse_duration,
    _infer_degrees,
    _infer_fields,
    _extract_perks,
    _extract_responsibilities,
    _extract_openings,
    _normalize_location,
    _generate_oid,
)


def test_parse_stipend_unpaid_and_performance() -> None:
    assert _parse_stipend("Unpaid") == {
        "type": "unpaid", "amount": 0, "currency": "INR", "period": "monthly"
    }
    assert _parse_stipend("Performance Based") == {
        "type": "performance_based", "amount": 0, "currency": "INR", "period": "monthly"
    }
    assert _parse_stipend("Not Disclosed") == {
        "type": "not_disclosed", "amount": 0, "currency": "INR", "period": "monthly"
    }


def test_parse_stipend_lpa_and_decimals() -> None:
    res1 = _parse_stipend("3.5 LPA")
    assert res1["type"] == "paid"
    assert res1["amount"] == 350000
    assert res1["period"] == "yearly"

    res2 = _parse_stipend("2.4 Lacs")
    assert res2["type"] == "paid"
    assert res2["amount"] == 240000
    assert res2["period"] == "yearly"

    res3 = _parse_stipend("12,000 /month")
    assert res3["type"] == "paid"
    assert res3["amount"] == 12000
    assert res3["period"] == "monthly"

    res4 = _parse_stipend("3,000 /week")
    assert res4["type"] == "paid"
    assert res4["amount"] == 3000
    assert res4["period"] == "weekly"

    res5 = _parse_stipend("50,000 lump sum")
    assert res5["type"] == "paid"
    assert res5["amount"] == 50000
    assert res5["period"] == "lump_sum"


def test_parse_duration() -> None:
    assert _parse_duration("6 Months") == {"value": 6, "unit": "months"}
    assert _parse_duration("8 Weeks") == {"value": 8, "unit": "weeks"}
    assert _parse_duration("1 Year") == {"value": 1, "unit": "years"}
    assert _parse_duration("") == {"value": 0, "unit": "months"}


def test_parse_date_and_relative() -> None:
    d1 = _parse_date("15 Jan 2026")
    assert d1 is not None and d1.day == 15 and d1.month == 1 and d1.year == 2026

    d2 = _parse_date("1st August 2026")
    assert d2 is not None and d2.day == 1 and d2.month == 8 and d2.year == 2026

    rel_today = _parse_relative_date("Today")
    assert rel_today is not None and rel_today.date() == datetime.now().date()

    rel_yesterday = _parse_relative_date("Yesterday")
    assert rel_yesterday is not None and (datetime.now() - rel_yesterday).days <= 2

    rel_days = _parse_relative_date("3 days ago")
    assert rel_days is not None and 2 <= (datetime.now() - rel_days).days <= 4


def test_location_normalization() -> None:
    loc1 = _normalize_location("Bangalore")
    assert loc1["city"] == "Bangalore"
    assert loc1["state"] == "Karnataka"
    assert loc1["isRemote"] is False

    loc2 = _normalize_location("Work from Home")
    assert loc2["isRemote"] is True

    loc3 = _normalize_location("Mumbai, Maharashtra")
    assert loc3["city"] == "Mumbai"
    assert loc3["state"] == "Maharashtra"


def test_extract_degrees_and_fields() -> None:
    text = "Candidate must have B.Tech or MCA in Computer Science or Information Technology."
    degs = _infer_degrees(text)
    assert "B.Tech" in degs or "MCA" in degs

    fields = _infer_fields(text)
    assert "Computer Science" in fields or "Information Technology" in fields


def test_extract_perks_and_responsibilities() -> None:
    text = "Perks include Certificate, Letter of Recommendation, Flexible hours, 5 days a week."
    perks = _extract_perks(text)
    assert "Certificate" in perks
    assert "Letter of Recommendation" in perks
    assert "Flexible hours" in perks

    desc = "- Develop REST APIs\n- Write unit tests\n- Maintain database schemas"
    resp = _extract_responsibilities(desc)
    assert len(resp) >= 3


def test_extract_openings() -> None:
    assert _extract_openings("Hiring 5 interns for summer batch") == 5
    assert _extract_openings("10 openings available") == 10
    assert _extract_openings("Immediate vacancy for 1 role") == 1


def test_generate_oid() -> None:
    oid1 = _generate_oid("internshala", "Dev", "Co", "https://link.com/1")
    oid2 = _generate_oid("internshala", "Dev", "Co", "https://link.com/1")
    oid3 = _generate_oid("internshala", "Dev", "Co", "https://link.com/2")
    assert len(oid1) == 24
    assert oid1 == oid2
    assert oid1 != oid3


def test_full_format_internship() -> None:
    raw = {
        "title": "Full Stack Engineer Intern",
        "company": "NextGen AI Labs",
        "link": "https://nextgen.ai/careers/intern-1",
        "stipend": "₹ 25,000 /month",
        "duration": "3 Months",
        "location": "Pune",
        "date_posted": "2 days ago",
        "deadline": "30 Oct 2026",
        "skills": ["Python", "FastAPI", "React", "Docker"],
        "description": "Selected intern's day-to-day responsibilities include:\n1. Building web applications.\n2. Working on backend APIs.\nPerks: Certificate, Letter of recommendation, Free snacks.",
        "openings": 3,
    }

    formatted = format_internship(raw, source="custom_scraper")

    assert formatted["name"] == "Full Stack Engineer Intern"
    assert formatted["company"] == "NextGen AI Labs"
    assert formatted["city"] == "Pune"
    assert formatted["state"] == "Maharashtra"
    assert formatted["stipend"]["amount"] == 25000
    assert formatted["stipend"]["period"] == "monthly"
    assert formatted["duration"]["value"] == 3
    assert formatted["openings"] == 3
    assert "Certificate" in formatted["perks"]
    assert len(formatted["skills"]) == 4
    assert formatted["source"] == "custom_scraper"
    assert formatted["isActive"] is True
    assert "_id" in formatted and "$oid" in formatted["_id"]
