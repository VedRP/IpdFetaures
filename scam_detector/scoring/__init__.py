"""
scam_detector.scoring
=====================
Scoring layer: takes a :class:`FeatureVector` and produces a risk score
plus a human-readable explanation.

Exports
-------
  RiskLabel          — Enum: LOW | MEDIUM | HIGH
  RulesResult        — Output of the deterministic rules engine
  RiskEngineResult   — Output of the ML risk engine
  ScamScoreResult    — Final combined result with explanation
  apply_rules        — Run deterministic rules
  apply_risk_engine  — Run ML risk model
  explain            — Build explanation from combined results
"""

from scam_detector.scoring.rules_engine import RulesResult, apply_rules
from scam_detector.scoring.risk_engine import RiskEngineResult, apply_risk_engine
from scam_detector.scoring.explain import ScamScoreResult, RiskLabel, explain

__all__: list[str] = [
    "RiskLabel",
    "RulesResult",
    "RiskEngineResult",
    "ScamScoreResult",
    "apply_rules",
    "apply_risk_engine",
    "explain",
]
