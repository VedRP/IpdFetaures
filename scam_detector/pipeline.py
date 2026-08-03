"""
pipeline.py
-----------
Top-level orchestrator for the scam-detection pipeline.

Execution order
---------------
  1. load        — accept a raw internship dict
  2. remediate   — Phase 1 data cleanup  (data_quality.remediate)
  3. features    — extract all signals   (features.extract_all)
  4. score       — rules + ML engine     (scoring.apply_rules / apply_risk_engine)
  5. explain     — combine & label       (scoring.explain)
  6. output      — return ScamScoreResult

Usage
-----
    from scam_detector import ScamDetectorPipeline, ScamScoreResult

    pipeline = ScamDetectorPipeline()
    result: ScamScoreResult = pipeline.run(raw_dict)
"""

from __future__ import annotations

from typing import Any

from scam_detector.config import Config, cfg as default_cfg
from scam_detector.data_quality.remediate import remediate_record as remediate
from scam_detector.features import extract_all
from scam_detector.scoring.rules_engine import apply_rules
from scam_detector.scoring.risk_engine import apply_risk_engine
from scam_detector.scoring.explain import ScamScoreResult, explain


class ScamDetectorPipeline:
    """
    Stateless pipeline wrapper.

    Parameters
    ----------
    config:
        Override the module-level singleton if you need custom thresholds
        or feature-flag combinations (e.g. in tests).
    """

    def __init__(self, config: Config | None = None) -> None:
        self.config: Config = config or default_cfg

    def run(self, raw: dict[str, Any]) -> ScamScoreResult:
        """
        Run the full pipeline against a single raw internship dict.

        Logic to be implemented — currently passes data through each stage
        and returns a default (all-safe) :class:`ScamScoreResult`.
        """
        # Stage 1: remediate
        record = remediate(raw)

        # Stage 2: extract features
        features = extract_all(record)

        # Stage 3: deterministic rules
        rules_result = apply_rules(features)

        # Stage 4: ML risk engine
        risk_result = apply_risk_engine(features)

        # Stage 5: combine & explain
        result = explain(rules_result, risk_result, features)

        return result
