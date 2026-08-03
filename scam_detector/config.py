"""
config.py
---------
Single source of truth for all tunable knobs:
thresholds, weights, and feature flags.

Import anywhere via:
    from scam_detector.config import cfg
"""

from __future__ import annotations
from pydantic import BaseModel, Field


class ScoringWeights(BaseModel):
    """Relative weights applied when combining individual risk signals."""

    text_weight: float = Field(default=0.25, ge=0.0, le=1.0)
    company_weight: float = Field(default=0.20, ge=0.0, le=1.0)
    url_weight: float = Field(default=0.20, ge=0.0, le=1.0)
    stipend_weight: float = Field(default=0.15, ge=0.0, le=1.0)
    temporal_weight: float = Field(default=0.10, ge=0.0, le=1.0)
    structural_weight: float = Field(default=0.10, ge=0.0, le=1.0)


class RuleWeights(BaseModel):
    """
    Per-rule weights for the deterministic rules engine.

    Each value is the risk contribution [0, 1] added when the rule fires.
    Tune here without touching rule logic.

    Rationale behind defaults
    -------------------------
    hard_disqualifying_signals : 0.95  — near-automatic escalation to human
                                         review; only 1 other signal can override
    cross_company_duplicate     : 0.80  — same script / multiple shells is the
                                         strongest single fraud indicator
    typosquat_domain            : 0.70  — off-platform mismatch is strong
    extreme_stipend_outlier     : 0.45  — both directions are suspicious but
                                         context matters; moderate weight
    mass_openings_vague_role    : 0.40  — combined heuristic; moderate
    stipend_perk_contradiction  : 0.35  — data quality issue, not certain fraud
    unverifiable_company        : 0.10  — scraper noise, very low weight;
                                         reduces CONFIDENCE, not fraud score
    """

    hard_disqualifying_signals: float = Field(default=0.95, ge=0.0, le=1.0)
    cross_company_duplicate: float = Field(default=0.80, ge=0.0, le=1.0)
    typosquat_domain: float = Field(default=0.70, ge=0.0, le=1.0)
    extreme_stipend_outlier: float = Field(default=0.45, ge=0.0, le=1.0)
    mass_openings_vague_role: float = Field(default=0.40, ge=0.0, le=1.0)
    stipend_perk_contradiction: float = Field(default=0.35, ge=0.0, le=1.0)
    unverifiable_company: float = Field(default=0.10, ge=0.0, le=1.0)


class RuleThresholds(BaseModel):
    """
    Per-rule numeric thresholds, configurable without touching rule logic.
    """

    # ExtremeStipendOutlierRule: |z-score| must exceed this to trigger
    stipend_zscore_threshold: float = Field(default=3.0, ge=0.0)

    # TyposquatDomainRule: domain_company_similarity below this on off-platform link
    typosquat_similarity_threshold: float = Field(default=0.35, ge=0.0, le=1.0)

    # MassOpeningsVagueRoleRule: openings z-score above this AND genericity above this
    mass_openings_zscore_threshold: float = Field(default=2.0, ge=0.0)
    mass_openings_genericity_threshold: float = Field(default=0.65, ge=0.0, le=1.0)


class Thresholds(BaseModel):
    """Decision boundaries for risk classification."""

    auto_approve_below: float = Field(default=0.25, ge=0.0, le=1.0)
    pending_review_below: float = Field(default=0.55, ge=0.0, le=1.0)
    # scores >= pending_review_below are classified as high-risk / auto-rejected


class FeatureFlags(BaseModel):
    """Toggle individual feature groups on/off without changing pipeline code."""

    enable_text_features: bool = True
    enable_company_features: bool = True
    enable_url_features: bool = True
    enable_stipend_features: bool = True
    enable_temporal_features: bool = True
    enable_structural_features: bool = True
    enable_ml_risk_engine: bool = False  # off until a trained model is present


class Config(BaseModel):
    """Top-level config object — instantiate once and share."""

    weights: ScoringWeights = Field(default_factory=ScoringWeights)
    rule_weights: RuleWeights = Field(default_factory=RuleWeights)
    rule_thresholds: RuleThresholds = Field(default_factory=RuleThresholds)
    thresholds: Thresholds = Field(default_factory=Thresholds)
    flags: FeatureFlags = Field(default_factory=FeatureFlags)


# Module-level singleton — override fields as needed in tests or via env vars.
cfg = Config()
