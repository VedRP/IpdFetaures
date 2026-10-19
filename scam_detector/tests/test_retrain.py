"""
test_retrain.py
----------------
Tests for retrain.py — the automated retraining ("self-learning") cycle:
promote votes, gate on data sufficiency, train a candidate, evaluate it
against the incumbent on a held-out split, and only promote if it's at
least as good.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scam_detector.config import Config
from scam_detector.feedback import FeedbackStore, ReviewFeedback
from scam_detector.retrain import (
    list_model_versions,
    rollback_to_version,
    run_retraining_cycle,
)


def _make_record(idx: int, is_scam: bool) -> dict:
    if is_scam:
        return {
            "_id": f"rec-{idx}",
            "name": "URGENT PAYMENT NEEDED FOR INTERNSHIP",
            "company": "Digital Marketing",
            "summary": "Pay Rs 5000 registration fee to get this internship. Send bank details.",
            "stipend": "Unpaid",
            "perks": ["Stipend"],
            "applyLink": "http://bit.ly/fake-link",
            "isRemote": True,
        }
    return {
        "_id": f"rec-{idx}",
        "name": "Software Engineering Intern",
        "company": "Google LLC",
        "summary": "Join our engineering team to build scalable systems in Python and C++.",
        "stipend": {"type": "fixed", "amount": 25000, "currency": "INR", "period": "monthly"},
        "perks": ["Certificate", "Letter of recommendation"],
        "applyLink": "https://careers.google.com/jobs/123",
        "isRemote": False,
        "skills": ["Python", "C++"],
        "field": ["Engineering"],
    }


def _make_config(tmp_path: Path, min_training_samples: int = 40) -> Config:
    cfg = Config()
    cfg.feedback.store_path = str(tmp_path / "feedback.jsonl")
    cfg.feedback.applicant_vote_store_path = str(tmp_path / "votes.jsonl")
    cfg.supervised.model_path = str(tmp_path / "models" / "supervised_model.joblib")
    cfg.supervised.versions_dir = str(tmp_path / "models" / "versions")
    cfg.supervised.retrain_history_path = str(tmp_path / "models" / "retrain_history.jsonl")
    cfg.supervised.min_training_samples = min_training_samples
    cfg.supervised.holdout_fraction = 0.25
    return cfg


def _seed_balanced_feedback(cfg: Config, n: int) -> list[dict]:
    feedback_store = FeedbackStore(cfg.feedback.store_path)
    records = []
    for i in range(n):
        is_scam = (i % 2 == 0)
        records.append(_make_record(i, is_scam))
        decision = "confirmed_scam" if is_scam else "confirmed_legit"
        feedback_store.record_feedback(
            ReviewFeedback(record_id=f"rec-{i}", reviewer_decision=decision)
        )
    return records


class TestRunRetrainingCycleGating:
    def test_refuses_with_insufficient_labels(self, tmp_path: Path):
        cfg = _make_config(tmp_path, min_training_samples=100)
        records = _seed_balanced_feedback(cfg, 10)
        result = run_retraining_cycle(records, config=cfg)
        assert result.trained is False
        assert "insufficient" in result.reason.lower() or "need" in result.reason.lower()

    def test_refuses_with_severe_class_imbalance(self, tmp_path: Path):
        cfg = _make_config(tmp_path, min_training_samples=20)
        feedback_store = FeedbackStore(cfg.feedback.store_path)
        records = []
        # 38 legit, 2 scam -> minority well under the 5% default floor is
        # not quite true at 2/40=5%, so push further to 1/40=2.5%.
        for i in range(39):
            records.append(_make_record(i, is_scam=False))
            feedback_store.record_feedback(
                ReviewFeedback(record_id=f"rec-{i}", reviewer_decision="confirmed_legit")
            )
        records.append(_make_record(39, is_scam=True))
        feedback_store.record_feedback(
            ReviewFeedback(record_id="rec-39", reviewer_decision="confirmed_scam")
        )
        result = run_retraining_cycle(records, config=cfg)
        assert result.trained is False
        assert "minority" in result.reason.lower() or "imbalance" in result.reason.lower()


class TestRunRetrainingCycleTrainingAndPromotion:
    def test_trains_and_promotes_when_no_incumbent_exists(self, tmp_path: Path):
        cfg = _make_config(tmp_path, min_training_samples=40)
        records = _seed_balanced_feedback(cfg, 60)

        result = run_retraining_cycle(records, config=cfg)

        assert result.trained is True
        assert result.promoted is True
        assert result.candidate_auc is not None
        assert result.incumbent_auc is None
        assert Path(cfg.supervised.model_path).exists()
        assert result.model_version_path is not None
        assert Path(result.model_version_path).exists()

    def test_promotes_only_logs_once_per_cycle(self, tmp_path: Path):
        cfg = _make_config(tmp_path, min_training_samples=40)
        records = _seed_balanced_feedback(cfg, 60)
        run_retraining_cycle(records, config=cfg)

        from scam_detector.retrain import load_retrain_history

        history = load_retrain_history(cfg.supervised.retrain_history_path)
        assert len(history) == 1
        assert history[0].trained is True

    def test_second_cycle_evaluates_against_incumbent(self, tmp_path: Path):
        cfg = _make_config(tmp_path, min_training_samples=40)
        records = _seed_balanced_feedback(cfg, 60)

        first = run_retraining_cycle(records, config=cfg)
        assert first.promoted is True

        # More of the same clean signal -> candidate should still be
        # reasonable and, with no incumbent regression, gets promoted again.
        more_records = _seed_balanced_feedback(cfg, 90)  # overlapping ids re-recorded is fine; store is append-only
        second = run_retraining_cycle(more_records, config=cfg)

        assert second.trained is True
        assert second.incumbent_auc is not None


class TestModelVersioningAndRollback:
    def test_list_model_versions_returns_created_versions(self, tmp_path: Path):
        cfg = _make_config(tmp_path, min_training_samples=40)
        records = _seed_balanced_feedback(cfg, 60)
        run_retraining_cycle(records, config=cfg)

        versions = list_model_versions(cfg)
        assert len(versions) == 1

    def test_rollback_restores_a_previous_version(self, tmp_path: Path):
        cfg = _make_config(tmp_path, min_training_samples=40)
        records = _seed_balanced_feedback(cfg, 60)
        result = run_retraining_cycle(records, config=cfg)

        live_before = Path(cfg.supervised.model_path).read_bytes()
        version_bytes = Path(result.model_version_path).read_bytes()
        assert live_before == version_bytes

        rollback_to_version(result.model_version_path, config=cfg)
        assert Path(cfg.supervised.model_path).read_bytes() == version_bytes

    def test_rollback_raises_on_missing_version(self, tmp_path: Path):
        cfg = _make_config(tmp_path, min_training_samples=40)
        with pytest.raises(FileNotFoundError):
            rollback_to_version(tmp_path / "does_not_exist.joblib", config=cfg)
