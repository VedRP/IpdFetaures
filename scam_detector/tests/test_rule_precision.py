"""Tests for scoring/rule_precision.py — adaptive, feedback-driven rule weights."""

from __future__ import annotations

import pytest

from scam_detector.config import Config
from scam_detector.feedback import FeedbackStore, ReviewFeedback
from scam_detector.scoring.rule_precision import (
    RuleFiringStore,
    RulePrecisionStats,
    compute_rule_precision,
    get_adjusted_config,
    get_adjusted_rule_weights,
)


@pytest.fixture
def firing_store(tmp_path):
    return RuleFiringStore(tmp_path / "firings.jsonl")


@pytest.fixture
def feedback_store(tmp_path):
    return FeedbackStore(tmp_path / "feedback.jsonl")


class TestComputeRulePrecision:
    def test_ignores_firings_with_no_feedback(self, firing_store, feedback_store):
        firing_store.log_firing("r1", ["some_rule"])
        stats = compute_rule_precision(firing_store, feedback_store)
        assert stats == {}

    def test_counts_confirmed_scam_and_cleared(self, firing_store, feedback_store):
        firing_store.log_firing("r1", ["suspicious_recruiter_contact"])
        firing_store.log_firing("r2", ["suspicious_recruiter_contact"])
        feedback_store.record_feedback(
            ReviewFeedback(record_id="r1", reviewer_decision="confirmed_scam")
        )
        feedback_store.record_feedback(
            ReviewFeedback(record_id="r2", reviewer_decision="false_positive")
        )
        stats = compute_rule_precision(firing_store, feedback_store)
        s = stats["suspicious_recruiter_contact"]
        assert s.weighted_confirmed_scam == 1.0
        assert s.weighted_cleared == 1.0
        assert s.observations == 2.0

    def test_low_confidence_feedback_contributes_less(self, firing_store, feedback_store):
        firing_store.log_firing("r1", ["unverifiable_company"])
        feedback_store.record_feedback(
            ReviewFeedback(
                record_id="r1",
                reviewer_decision="false_positive",
                confidence=0.2,
                source="applicant_vote_aggregate",
            )
        )
        stats = compute_rule_precision(firing_store, feedback_store)
        assert stats["unverifiable_company"].weighted_cleared == pytest.approx(0.2)


class TestGetAdjustedRuleWeights:
    def test_unobserved_rule_keeps_default(self):
        from scam_detector.config import RuleWeights

        base = RuleWeights()
        adjusted = get_adjusted_rule_weights(base, {}, min_observations=20)
        assert adjusted.suspicious_recruiter_contact == base.suspicious_recruiter_contact

    def test_rule_below_min_observations_keeps_default(self):
        from scam_detector.config import RuleWeights

        base = RuleWeights()
        stats = {
            "suspicious_recruiter_contact": RulePrecisionStats(
                rule_id="suspicious_recruiter_contact",
                weighted_confirmed_scam=1.0,
                weighted_cleared=1.0,
            )
        }
        adjusted = get_adjusted_rule_weights(base, stats, min_observations=20)
        assert adjusted.suspicious_recruiter_contact == base.suspicious_recruiter_contact

    def test_rule_with_poor_precision_shrinks_toward_lower_weight(self):
        from scam_detector.config import RuleWeights

        base = RuleWeights()
        base_weight = base.suspicious_recruiter_contact
        # 100 observations, almost all cleared (false_positive) -> low precision
        stats = {
            "suspicious_recruiter_contact": RulePrecisionStats(
                rule_id="suspicious_recruiter_contact",
                weighted_confirmed_scam=5.0,
                weighted_cleared=95.0,
            )
        }
        adjusted = get_adjusted_rule_weights(base, stats, min_observations=20)
        assert adjusted.suspicious_recruiter_contact < base_weight

    def test_rule_with_perfect_precision_shrinks_toward_higher_weight(self):
        from scam_detector.config import RuleWeights

        base = RuleWeights(unverifiable_company=0.10)
        stats = {
            "unverifiable_company": RulePrecisionStats(
                rule_id="unverifiable_company",
                weighted_confirmed_scam=100.0,
                weighted_cleared=0.0,
            )
        }
        adjusted = get_adjusted_rule_weights(base, stats, min_observations=20)
        assert adjusted.unverifiable_company > 0.10

    def test_unknown_rule_id_is_ignored(self):
        from scam_detector.config import RuleWeights

        base = RuleWeights()
        stats = {
            "nonexistent_rule": RulePrecisionStats(
                rule_id="nonexistent_rule",
                weighted_confirmed_scam=100.0,
                weighted_cleared=0.0,
            )
        }
        # Should not raise.
        get_adjusted_rule_weights(base, stats, min_observations=20)


class TestGetAdjustedConfig:
    def test_disabled_by_default_returns_unmodified_config(self, firing_store, feedback_store):
        cfg = Config()
        assert cfg.flags.enable_adaptive_rule_weights is False
        adjusted = get_adjusted_config(cfg, firing_store, feedback_store)
        assert adjusted is cfg

    def test_enabled_with_no_data_returns_same_weights(self, firing_store, feedback_store):
        cfg = Config()
        cfg.flags.enable_adaptive_rule_weights = True
        adjusted = get_adjusted_config(cfg, firing_store, feedback_store)
        assert adjusted.rule_weights == cfg.rule_weights

    def test_enabled_with_data_adjusts_weights(self, firing_store, feedback_store):
        cfg = Config()
        cfg.flags.enable_adaptive_rule_weights = True
        cfg.feedback.min_firing_observations_for_adjustment = 5

        for i in range(10):
            firing_store.log_firing(f"r{i}", ["suspicious_recruiter_contact"])
            feedback_store.record_feedback(
                ReviewFeedback(record_id=f"r{i}", reviewer_decision="false_positive")
            )

        adjusted = get_adjusted_config(cfg, firing_store, feedback_store)
        assert (
            adjusted.rule_weights.suspicious_recruiter_contact
            < cfg.rule_weights.suspicious_recruiter_contact
        )
        # Never mutates the original.
        assert cfg.rule_weights.suspicious_recruiter_contact == Config().rule_weights.suspicious_recruiter_contact
