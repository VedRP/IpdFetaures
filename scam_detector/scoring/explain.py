"""
explain.py
----------
Combines outputs from the rules engine and ML risk engine into a single
:class:`ScamScoreResult` with a human-readable explanation.

Planned logic (to be implemented):
  - Blend rules score and ML score using config weights
  - Map the blended score to a :class:`RiskLabel`
  - Produce an ordered list of top contributing signals
  - Emit a plain-English summary sentence
"""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class RiskLabel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ScoreContributor(BaseModel):
    """One signal that contributed to the final score."""

    source: str = Field(description="e.g. 'rules.RULE_PAY_TO_WORK' or 'ml_engine'")
    label: str = Field(description="Human-readable signal name")
    contribution: float = Field(ge=0.0, le=1.0)


class ScamScoreResult(BaseModel):
    """
    Final output of the scam-detection pipeline for a single internship.
    """

    final_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Blended risk score (0 = clean, 1 = definite scam)",
    )
    label: RiskLabel = Field(default=RiskLabel.LOW)
    is_hard_reject: bool = Field(
        default=False,
        description="Overrides label — reject immediately regardless of score",
    )
    top_contributors: list[ScoreContributor] = Field(default_factory=list)
    summary: str = Field(
        default="",
        description="One-sentence plain-English explanation of the verdict",
    )
    rules_score: float = Field(default=0.0, ge=0.0, le=1.0)
    ml_score: float = Field(default=0.5, ge=0.0, le=1.0)


def explain(
    rules_result: object,      # RulesResult
    risk_result: object,       # RiskEngineResult
    features: object,          # FeatureVector
) -> ScamScoreResult:
    """
    Combine *rules_result* and *risk_result* into a :class:`ScamScoreResult`.

    Logic to be implemented — currently returns a zero-risk skeleton.
    """
    # TODO: blend scores, map to label, build contributors list, write summary
    return ScamScoreResult()
