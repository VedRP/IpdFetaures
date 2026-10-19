"""
rule_precision.py
-----------------
Lets confirmed_legit / false_positive feedback actively dampen a rule's
weight instead of just sitting in the FeedbackStore unused.

Every pipeline run logs which rules fired for which record_id
(``RuleFiringStore``). Once moderator/applicant-vote feedback exists for
those same record_ids, we can measure each rule's *live precision* — of the
times it fired, how often was the record later confirmed a scam vs. cleared
or overturned — and shrink its noisy-OR weight toward that observed
precision. A rule that fires constantly on legitimate listings gets quietly
dialed down; a rule that's always right when it fires can be trusted more.

This is a Beta-Bernoulli style online update: each rule starts at its
hand-tuned config.py weight (the prior) and only moves once enough
feedback-joined observations exist (``min_observations``), with the amount
of movement controlled by how much evidence has accumulated — a rule with
only a handful of observations barely moves, one with hundreds moves close
to its measured precision.

Retraining/adjustment is meant to run offline on a schedule (e.g. before
each deploy or nightly batch), not applied automatically mid-request — see
``get_adjusted_config``. It is entirely opt-in via
``cfg.flags.enable_adaptive_rule_weights`` (default off) until validated
against real feedback volume.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from scam_detector.config import Config, RuleWeights, cfg as _default_cfg
from scam_detector.feedback import FeedbackStore

log = logging.getLogger("scam_detector.scoring.rule_precision")

# Beta prior — equivalent to having "seen" this many pseudo-observations
# split evenly between scam/not-scam before any real feedback exists. Keeps
# a rule with 1-2 real observations from swinging to 0.0 or 1.0 precision.
_PRIOR_ALPHA = 2.0
_PRIOR_BETA = 2.0

# How much weight to put on observed precision vs. the config.py prior as
# evidence accumulates. At `min_observations` confidence-weighted
# observations, the rule is ~50% shrunk toward measured precision; it
# approaches fully data-driven only with substantially more than that.
_SHRINKAGE_SATURATION_MULTIPLIER = 4.0


class RuleFiring(BaseModel):
    """One pipeline run's record of which rules fired for one record."""

    record_id: str
    triggered_rule_ids: list[str] = Field(default_factory=list)


class RuleFiringStore:
    """Append-only JSONL store of rule firings, one line per scored record."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log_firing(self, record_id: str, triggered_rule_ids: list[str]) -> None:
        event = RuleFiring(record_id=record_id, triggered_rule_ids=triggered_rule_ids)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(event.model_dump_json() + "\n")

    def load_firings(self) -> list[RuleFiring]:
        if not self.path.exists():
            return []
        firings: list[RuleFiring] = []
        with self.path.open(encoding="utf-8") as fh:
            for lineno, raw in enumerate(fh, start=1):
                line = raw.strip()
                if not line:
                    continue
                try:
                    firings.append(RuleFiring.model_validate_json(line))
                except Exception as exc:
                    log.warning(
                        "Skipping malformed rule firing at %s:%d (%s)", self.path, lineno, exc
                    )
        return firings


class RulePrecisionStats(BaseModel):
    """Live precision stats for a single rule, from feedback-joined firings."""

    rule_id: str
    weighted_fires: float = 0.0
    weighted_confirmed_scam: float = 0.0
    weighted_cleared: float = 0.0  # false_positive or confirmed_legit

    @property
    def observations(self) -> float:
        """Confidence-weighted feedback-joined firing count."""
        return self.weighted_confirmed_scam + self.weighted_cleared

    @property
    def precision(self) -> float:
        """Beta-smoothed precision: P(scam | this rule fired)."""
        return (self.weighted_confirmed_scam + _PRIOR_ALPHA) / (
            self.observations + _PRIOR_ALPHA + _PRIOR_BETA
        )


def compute_rule_precision(
    firing_store: RuleFiringStore,
    feedback_store: FeedbackStore,
) -> dict[str, RulePrecisionStats]:
    """
    Join logged rule firings against feedback outcomes to compute each
    rule's live, confidence-weighted precision.

    Firings whose record_id has no feedback yet are ignored (they carry no
    information either way) — only feedback-joined firings count.
    """
    firings = firing_store.load_firings()
    if not firings:
        return {}

    feedback_by_record: dict[str, Any] = {}
    for fb in feedback_store.load_feedback_history():
        feedback_by_record[fb.record_id] = fb  # last write wins, same as build_training_labels

    stats: dict[str, RulePrecisionStats] = {}
    for firing in firings:
        fb = feedback_by_record.get(firing.record_id)
        if fb is None:
            continue
        for rule_id in firing.triggered_rule_ids:
            s = stats.setdefault(rule_id, RulePrecisionStats(rule_id=rule_id))
            s.weighted_fires += fb.confidence
            if fb.reviewer_decision == "confirmed_scam":
                s.weighted_confirmed_scam += fb.confidence
            else:  # false_positive or confirmed_legit
                s.weighted_cleared += fb.confidence

    return stats


def get_adjusted_rule_weights(
    base_weights: RuleWeights,
    precision_stats: dict[str, RulePrecisionStats],
    min_observations: int = 20,
) -> RuleWeights:
    """
    Shrink each rule's config.py weight toward its measured live precision,
    proportional to how much feedback-joined evidence has accumulated.

    A rule with fewer than ``min_observations`` weighted observations keeps
    its config.py default untouched — this is the same "genuinely inert
    until enough history accumulates" pattern used by ReputationStore.
    """
    adjusted = base_weights.model_copy(deep=True)

    for rule_id, stat in precision_stats.items():
        if not hasattr(adjusted, rule_id):
            continue  # unknown/renamed rule id — ignore rather than error
        if stat.observations < min_observations:
            continue

        base_weight = getattr(base_weights, rule_id)
        # Shrinkage factor grows from 0 at min_observations toward 1 as
        # observations grow past min_observations * _SHRINKAGE_SATURATION_MULTIPLIER.
        saturation_point = max(min_observations, 1) * _SHRINKAGE_SATURATION_MULTIPLIER
        shrinkage = min(1.0, (stat.observations - min_observations) / saturation_point)
        new_weight = (1.0 - shrinkage) * base_weight + shrinkage * stat.precision
        new_weight = max(0.0, min(1.0, new_weight))
        setattr(adjusted, rule_id, round(new_weight, 4))

        if abs(new_weight - base_weight) > 0.02:
            log.info(
                "Rule '%s' weight adjusted %.2f -> %.2f (precision=%.2f, observations=%.1f, shrinkage=%.2f)",
                rule_id, base_weight, new_weight, stat.precision, stat.observations, shrinkage,
            )

    return adjusted


def get_adjusted_config(
    base_cfg: Config | None = None,
    firing_store: RuleFiringStore | None = None,
    feedback_store: FeedbackStore | None = None,
) -> Config:
    """
    Return a copy of ``base_cfg`` with rule weights shrunk toward live,
    feedback-measured precision — or an unmodified copy if adaptive
    weighting is disabled or there isn't enough data yet.

    Never mutates the global config singleton; callers pass the returned
    copy to ``RulesEngine(config=...)`` for one scoring run.
    """
    cfg = base_cfg or _default_cfg
    if not cfg.flags.enable_adaptive_rule_weights:
        return cfg

    firing_store = firing_store or RuleFiringStore(cfg.feedback.rule_firing_log_path)
    feedback_store = feedback_store or FeedbackStore(cfg.feedback.store_path)

    try:
        precision_stats = compute_rule_precision(firing_store, feedback_store)
    except Exception as exc:
        log.warning("Failed to compute rule precision — using config.py defaults: %s", exc)
        return cfg

    if not precision_stats:
        return cfg

    adjusted_cfg = cfg.model_copy(deep=True)
    adjusted_cfg.rule_weights = get_adjusted_rule_weights(
        cfg.rule_weights,
        precision_stats,
        min_observations=cfg.feedback.min_firing_observations_for_adjustment,
    )
    return adjusted_cfg
