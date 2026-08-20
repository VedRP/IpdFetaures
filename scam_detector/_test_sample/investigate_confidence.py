"""Investigate confidence flat-line bug on real internships.json."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

# Repo layout: scam_detector package lives under iFind30/iFind30/
ROOT = Path(__file__).resolve().parents[2]  # iFind30/iFind30
PKG = ROOT / "scam_detector"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scam_detector.data_quality.remediate import remediate_record
from scam_detector.features.structural_features import field_completeness_score
from scam_detector.pipeline import ScamDetectorPipeline, process_records, load_records
from scam_detector.scoring.risk_engine import compute_confidence_score
from scam_detector.features import extract_all

INTERNSHIPS = ROOT / "internships.json"
OUT = PKG / "_test_sample" / "output_investigation.json"
SAMPLE = 30
SEED = 42


def flag_str(flags: dict) -> str:
    if not flags:
        return "(none)"
    keys = [
        "company_suspect",
        "degree_suspect_default",
        "summary_truncated",
        "deadline_missing",
        "responsibilities_cleaned",
        "date_possibly_inferred",
    ]
    present = [k for k in keys if flags.get(k)]
    return ",".join(present) if present else "(none)"


def main() -> None:
    print("=" * 80)
    print("STEP 1: Batch CLI pipeline")
    print("=" * 80)
    cmd = [
        sys.executable,
        "-m",
        "scam_detector.pipeline",
        str(INTERNSHIPS),
        str(OUT),
        "--sample",
        str(SAMPLE),
        "--seed",
        str(SEED),
    ]
    print("Command:", " ".join(cmd))
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    print(proc.stdout)
    if proc.stderr:
        print("STDERR:", proc.stderr)
    print("exit code:", proc.returncode)
    if proc.returncode != 0:
        sys.exit(proc.returncode)

    records = json.loads(OUT.read_text(encoding="utf-8"))[:SAMPLE]

    print("\n" + "=" * 80)
    print("STEP 2: Table (first 30 batch output records)")
    print("=" * 80)
    hdr = (
        f"{'_id':<28} {'company':<22} {'score':>6} {'conf':>6} {'dec':<6} "
        f"{'completeness':>12} {'flags'}"
    )
    print(hdr)
    print("-" * len(hdr))

    batch_trace = []
    for r in records:
        rid = str(r.get("_id", r.get("id", "?")))[:28]
        if isinstance(rid, dict):
            rid = str(rid.get("$oid", rid))[:28]
        company = str(r.get("company", ""))[:22]
        conf = r.get("confidence")
        score = r.get("scam_score")
        dec = r.get("decision", "")
        # Re-derive completeness + flags from raw fields in output
        flags = {k: v for k, v in r.items() if k in (
            "company_suspect", "degree_suspect_default", "summary_truncated",
            "deadline_missing", "responsibilities_cleaned", "date_possibly_inferred",
        ) or k == "_flags"}
        # remediation flags aren't in output — re-remediate for trace
        rem = remediate_record({k: v for k, v in r.items() if k not in (
            "scam_score", "decision", "explanation_summary", "confidence",
        )})
        comp = field_completeness_score(rem.record)
        batch_trace.append({
            "id": rid,
            "confidence": conf,
            "completeness": comp,
            "flags": rem.flags,
            "computed_conf": compute_confidence_score(rem, extract_all(rem, all_records=[rem.record])),
        })
        print(
            f"{rid:<28} {company:<22} {score:>6.1f} {conf:>6.4f} {dec:<6} "
            f"{comp:>12.4f} {flag_str(rem.flags)}"
        )

    conf_vals = [r.get("confidence") for r in records]
    distinct = sorted(set(conf_vals))
    print("\n" + "=" * 80)
    print("STEP 3: Distinct confidence values (batch output)")
    print("=" * 80)
    print(f"Count of records: {len(conf_vals)}")
    print(f"Distinct confidence values: {len(distinct)}")
    print("Values:", distinct)
    print("Frequency:", dict(Counter(conf_vals)))

    print("\n" + "=" * 80)
    print("STEP 4: Batch process_records vs ScamDetectorPipeline().run()")
    print("=" * 80)
    raw_sample = load_records(INTERNSHIPS)[:SAMPLE]
    # Use same seed subsample as pipeline
    import random
    rng = random.Random(SEED)
    if len(raw_sample) > SAMPLE:
        raw_sample = rng.sample(load_records(INTERNSHIPS), SAMPLE)

    batch_out = process_records(raw_sample)
    print(f"{'_id':<28} {'batch_conf':>10} {'single_conf':>12} {'match':>6} {'batch_comp':>10} {'single_comp':>12}")
    print("-" * 90)
    mismatches = 0
    for raw, bout in zip(raw_sample, batch_out):
        rid = str(raw.get("_id", "?"))[:28]
        if isinstance(raw.get("_id"), dict):
            rid = str(raw["_id"].get("$oid", raw["_id"]))[:28]
        single = ScamDetectorPipeline().run(raw)
        rem_b = remediate_record(raw)
        rem_s = remediate_record(raw)
        comp_b = extract_all(rem_b, all_records=[r.record for r in [rem_b]]).structural.field_completeness
        comp_s = extract_all(rem_s).structural.field_completeness
        match = abs(bout["confidence"] - single.confidence) < 1e-6
        if not match:
            mismatches += 1
        print(
            f"{rid:<28} {bout['confidence']:>10.4f} {single.confidence:>12.4f} "
            f"{str(match):>6} {comp_b:>10.4f} {comp_s:>10.4f}"
        )
    print(f"\nConfidence mismatches batch vs single: {mismatches}/{SAMPLE}")

    print("\n" + "=" * 80)
    print("STEP 5: SBERT / duplicate path check (no sentence-transformers)")
    print("=" * 80)
    try:
        from scam_detector.features.text_features import _sbert_model
        sbert = _sbert_model()
        print("sentence-transformers available:", sbert is not None)
    except Exception as e:
        print("sentence-transformers available: False", e)

    from scam_detector.pipeline import _build_duplicate_neighbors
    neighbors = _build_duplicate_neighbors([r.record for r in [remediate_record(r) for r in raw_sample[:5]]])
    print("Sample duplicate neighbors (first record):", neighbors[list(neighbors.keys())[0]][:3])

    # Check if duplicate/SBERT affects confidence directly
    print("\nNote: duplicate detection feeds cross_company_duplicate rule and anomaly score,")
    print("NOT compute_confidence_score directly. Checking anomaly score variance:")
    anomaly_vals = []
    for bout in batch_out:
        # anomaly not in output — re-run not trivial; use scam_score vs rules proxy
        pass
    print("(anomaly scores not persisted in output JSON — see batch logs)")


if __name__ == "__main__":
    main()
