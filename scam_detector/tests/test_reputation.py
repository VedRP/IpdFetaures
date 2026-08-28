"""
test_reputation.py
------------------
Tests for ReputationStore, company_reputation_score, and pipeline integration.
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

import pytest

from scam_detector.config import Config
from scam_detector.features.reputation_features import (
    CompanyReputation,
    ReputationStore,
    company_reputation_score,
)
from scam_detector.feedback import FeedbackStore, ReviewFeedback
from scam_detector.pipeline import process_records


def test_reputation_store_io(tmp_path: Path):
    store_file = tmp_path / "reputation.jsonl"
    store = ReputationStore(store_file)

    # Initial get is empty
    assert store.get_all_reputations() == {}

    # Update reputations
    rep1 = CompanyReputation(
        company="test company",
        first_seen="2026-08-01",
        total_postings=5,
        clear_count=4,
        review_count=1,
        block_count=0,
        average_scam_score=25.0,
        record_ids=["rec1", "rec2"],
    )
    store.update_reputations([rep1])

    all_reps = store.get_all_reputations()
    assert "test company" in all_reps
    assert all_reps["test company"].total_postings == 5
    assert all_reps["test company"].average_scam_score == 25.0

    # Overwrite update
    rep2 = CompanyReputation(
        company="test company",
        first_seen="2026-08-01",
        total_postings=6,
        clear_count=5,
        review_count=1,
        block_count=0,
        average_scam_score=22.0,
        record_ids=["rec1", "rec2", "rec3"],
    )
    store.update_reputations([rep2])

    all_reps = store.get_all_reputations()
    assert all_reps["test company"].total_postings == 6
    assert all_reps["test company"].average_scam_score == 22.0


def test_company_reputation_score(tmp_path: Path):
    rep_file = tmp_path / "reputation.jsonl"
    fb_file = tmp_path / "feedback.jsonl"

    rep_store = ReputationStore(rep_file)
    fb_store = FeedbackStore(fb_file)

    # First-seen return None
    assert company_reputation_score("unknown company", rep_store, fb_store) is None

    # Normal company with clean track record
    rep = CompanyReputation(
        company="clean company",
        first_seen="2026-08-01",
        total_postings=10,
        clear_count=10,
        review_count=0,
        block_count=0,
        average_scam_score=10.0,
        record_ids=["id1", "id2"],
    )
    rep_store.update_reputations([rep])

    score = company_reputation_score("clean company", rep_store, fb_store)
    # decision_risk = 0.0, avg_score_risk = 0.1, blended = 0.05
    assert score == 0.05

    # Company with confirmed scams in feedback store
    fb_store.record_feedback(
        ReviewFeedback(
            record_id="id1",
            reviewer_decision="confirmed_scam",
            reviewer_notes="Confirmed fraud",
        )
    )

    score_after_fb = company_reputation_score("clean company", rep_store, fb_store)
    assert score_after_fb == 1.0


def test_two_consecutive_pipeline_runs(tmp_path: Path):
    rep_file = tmp_path / "reputation.jsonl"
    fb_file = tmp_path / "feedback.jsonl"

    config = Config()
    config.reputation.store_path = str(rep_file)
    # We must also mock/monkeypatch feedback store path if process_records hardcodes it.
    # Wait, process_records instantiates FeedbackStore("scam_detector/feedback.jsonl").
    # Let's inspect pipeline.py line 477. It is:
    # feedback_store = FeedbackStore("scam_detector/feedback.jsonl")
    # To mock this, we can patch the path in test_pipeline.py or use monkeypatch.

    # Let's define the input listings for Run 1
    # Company A: clean listings
    # Company B: highly suspicious listings (triggering rules to get a high scam score)
    records_run1 = [
        {
            "_id": "run1-rec-a",
            "company": "Company A",
            "name": "Software Engineer Intern",
            "summary": "Join our software engineering team to write python code and tests.",
            "applyLink": "https://company-a.com/apply",
            "datePublished": "2026-08-01",
            "stipend": {"type": "paid", "amount": {"min": 10000, "max": 10000, "period": "month"}},
            "perks": ["Certificate"],
        },
        {
            "_id": "run1-rec-b",
            "company": "Company B",
            "name": "EASY MONEY URGENT CLICK NOW!!!",
            "summary": "MAKE $5000 A DAY SEND RESUME!!!",
            "applyLink": "https://bit.ly/scam-link-easy-money",
            "datePublished": "2026-08-01",
            "stipend": {"type": "paid", "amount": {"min": 5000000, "max": 5000000, "period": "month"}},  # Extreme stipend outlier
            "openings": 500,  # Mass openings
            "skills": [],
        }
    ]

    # Run 1
    outputs_run1 = process_records(records_run1, config=config)

    # Verify reputation store file was created and contains data for both companies
    assert rep_file.exists()
    rep_store = ReputationStore(rep_file)
    reps = rep_store.get_all_reputations()
    assert "company a" in reps
    assert "company b" in reps

    # Verify decisions
    dec_a1 = outputs_run1[0]["decision"]
    dec_b1 = outputs_run1[1]["decision"]

    # Since it was the first run, the reputation store wasn't populated prior to scoring,
    # so reputation score should not have impacted the scores.

    # Run 2: overlapping data with new listings for the same companies
    records_run2 = [
        {
            "_id": "run2-rec-a",
            "company": "Company A",
            "name": "Developer Intern",
            "summary": "Write tests, debug code, and work with git repository.",
            "applyLink": "https://company-a.com/apply-new",
            "datePublished": "2026-08-02",
            "stipend": {"type": "paid", "amount": {"min": 10000, "max": 10000, "period": "month"}},
            "perks": ["Certificate"],
        },
        {
            "_id": "run2-rec-b",
            "company": "Company B",
            "name": "Another great money making role",
            "summary": "Urgent recruitment make money fast.",
            "applyLink": "https://bit.ly/scam-link-fast-money",
            "datePublished": "2026-08-02",
            "stipend": {"type": "paid", "amount": {"min": 6000000, "max": 6000000, "period": "month"}},
            "openings": 450,
            "skills": [],
        }
    ]

    outputs_run2 = process_records(records_run2, config=config)

    # The scores from Run 2 should be influenced by the reputation from Run 1.
    # Company A had a clear decision in Run 1, so it should have a low reputation score (trust bonus).
    # Company B had a high risk decision, so it should have a higher reputation score.
    # Let's verify that the reputation store updated again and total postings became 2.
    reps2 = rep_store.get_all_reputations()
    assert reps2["company a"].total_postings == 2
    assert reps2["company b"].total_postings == 2
