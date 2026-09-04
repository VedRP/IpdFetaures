"""
test_benchmark.py
-----------------
Unit tests for the Kaggle benchmark module:
  - Schema mapping (map_kaggle_row_to_ifind)
  - Benchmark classification metrics (compute_benchmark_metrics)
  - Report formatting (generate_markdown_benchmark_report)
"""

from __future__ import annotations

import pytest

from scam_detector.tools.benchmark_kaggle import (
    BenchmarkMetrics,
    compute_benchmark_metrics,
    generate_markdown_benchmark_report,
    map_kaggle_row_to_ifind,
)


def test_map_kaggle_row_legitimate() -> None:
    row = {
        "posting_date": "2026-08-15",
        "internship_title": "Software Engineer Intern",
        "work_mode": "Remote",
        "industry": "IT",
        "location": "Bangalore",
        "company_name": "Infosys Ltd",
        "stipend": 25000.0,
        "payment_required": 0,
        "registration_fee": 0,
        "fake_certificate_offer": 0,
        "vague_description_score": 10,
        "urgency_score": 5,
        "keyword_spam_score": 10,
        "phishing_language_score": 5,
        "recruiter_email_type": "Corporate",
        "suspicious_email_domain": 0,
        "is_fake_posting": 0,
        "fraud_score": 12.5,
    }

    mapped = map_kaggle_row_to_ifind(row, 1)
    assert mapped["_id"] == "kaggle_1_2026-08-15"
    assert mapped["name"] == "Software Engineer Intern"
    assert mapped["company"] == "Infosys Ltd"
    assert mapped["isRemote"] is True
    assert mapped["stipend"] == 25000.0
    assert mapped["is_fake_posting"] == 0
    assert "https://www.infosys" in mapped["applyLink"]
    assert mapped["payment_required"] == 0


def test_map_kaggle_row_fraudulent() -> None:
    row = {
        "posting_date": "2026-08-20",
        "internship_title": "Data Entry Specialist",
        "work_mode": "Remote",
        "industry": "Staffing",
        "location": "Delhi",
        "company_name": "QuickHire Solutions",
        "stipend": 60000.0,
        "payment_required": 1,
        "registration_fee": 2500.0,
        "fake_certificate_offer": 1,
        "vague_description_score": 75,
        "urgency_score": 85,
        "keyword_spam_score": 60,
        "phishing_language_score": 80,
        "recruiter_email_type": "Free",
        "suspicious_email_domain": 1,
        "is_fake_posting": 1,
        "fraud_score": 92.0,
    }

    mapped = map_kaggle_row_to_ifind(row, 2)
    assert mapped["payment_required"] == 1
    assert mapped["registration_fee"] == 2500.0
    assert mapped["fake_certificate_offer"] == 1
    assert mapped["is_fake_posting"] == 1
    assert "careers-portal.xyz" in mapped["applyLink"]
    assert "Mandatory registration fee of INR 2500.00" in mapped["summary"]
    assert "WhatsApp" in mapped["summary"]


def test_compute_benchmark_metrics_balanced() -> None:
    scored_records = [
        {"is_fake_posting": 1, "scam_score": 85.0, "decision": "block"},
        {"is_fake_posting": 1, "scam_score": 75.0, "decision": "block"},
        {"is_fake_posting": 1, "scam_score": 40.0, "decision": "review"},  # FN for thr=50
        {"is_fake_posting": 0, "scam_score": 15.0, "decision": "clear"},
        {"is_fake_posting": 0, "scam_score": 20.0, "decision": "clear"},
        {"is_fake_posting": 0, "scam_score": 65.0, "decision": "review"},  # FP for thr=50
    ]

    metrics = compute_benchmark_metrics(scored_records, threshold=50.0, duration=0.6)
    assert metrics.total_samples == 6
    assert metrics.true_positives == 2
    assert metrics.false_positives == 1
    assert metrics.true_negatives == 2
    assert metrics.false_negatives == 1
    assert metrics.accuracy == round(4 / 6, 4)
    assert metrics.precision == round(2 / 3, 4)
    assert metrics.recall == round(2 / 3, 4)
    assert metrics.f1_score == round(2 / 3, 4)
    assert metrics.block_count == 2
    assert metrics.review_count == 2
    assert metrics.clear_count == 2


def test_generate_markdown_benchmark_report() -> None:
    metrics = BenchmarkMetrics(
        total_samples=100,
        legitimate_samples=50,
        scam_samples=50,
        true_positives=45,
        false_positives=5,
        true_negatives=45,
        false_negatives=5,
        accuracy=0.90,
        precision=0.90,
        recall=0.90,
        specificity=0.90,
        f1_score=0.90,
        f2_score=0.90,
        decision_threshold=50.0,
        duration_seconds=1.25,
        throughput_records_per_sec=80.0,
        latency_ms_per_record=12.5,
        clear_count=45,
        review_count=10,
        block_count=45,
    )

    report = generate_markdown_benchmark_report(metrics, "Synthetic Test Set")
    assert "# 🛡️ iFind Scam Detection Engine Benchmark Report" in report
    assert "**Total Samples Evaluated**: 100 listings" in report
    assert "**Accuracy** | **90.00%**" in report
    assert "TN = 45" in report
    assert "TP = 45" in report
    assert "Blocked (High Risk): 45" in report
