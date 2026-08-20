import json
import subprocess
import sys
from pathlib import Path

tmp = Path(__file__).parent
records = [
    {
        "_id": "demo-clean",
        "name": "Backend Development Intern",
        "company": "BrightLabs Pvt Ltd",
        "summary": "Work with our engineering team on backend APIs in Python.",
        "applyLink": "https://internshala.com/internship/detail/demo-clean",
        "datePublished": "2026-05-01",
        "deadlineDate": "2026-06-15",
        "isRemote": True,
        "stipend": {
            "type": "paid",
            "amount": {"min": 12000, "max": 12000, "period": "month"},
            "currency": "INR",
        },
        "duration": {"value": 3, "unit": "months"},
        "skills": ["Python"],
        "degree": ["B.Tech"],
        "field": ["Computer Science"],
        "tags": ["internship"],
        "openings": 2,
        "responsibilities": ["Build features"],
        "perks": ["Certificate"],
    },
    {
        "_id": "demo-scam",
        "name": "Marketing Intern",
        "company": "QuickHire Shell",
        "summary": (
            "Pay a security deposit of Rs 2000 and submit Aadhaar before joining. URGENT!!!"
        ),
        "applyLink": "https://totally-legit-jobs.xyz/apply",
        "datePublished": "2026-05-01",
        "isRemote": True,
        "stipend": {
            "type": "paid",
            "amount": {"min": 50000, "max": 50000, "period": "month"},
            "currency": "INR",
        },
        "duration": {"value": 1, "unit": "months"},
        "skills": ["Marketing"],
        "field": ["Marketing"],
        "tags": ["internship"],
        "openings": 100,
    },
]

inp = tmp / "input.json"
out = tmp / "output.json"
inp.write_text(json.dumps(records, indent=2), encoding="utf-8")
subprocess.run(
    [sys.executable, "-m", "scam_detector.pipeline", str(inp), str(out)],
    check=True,
)
for r in json.loads(out.read_text(encoding="utf-8")):
    print(
        f"{r['_id']}: score={r['scam_score']} decision={r['decision']} "
        f"conf={r['confidence']:.2f}"
    )
    print(f"  {r['explanation_summary']}")
