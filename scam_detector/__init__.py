"""
scam_detector
=============
Internship scam-detection and data-quality pipeline for iFind.

Quick start
-----------
    from scam_detector import ScamDetectorPipeline, ScamScoreResult, FeatureVector

    result: ScamScoreResult = ScamDetectorPipeline().run(raw_internship_dict)

Sub-packages
------------
  scam_detector.data_quality  — Phase 1 remediation / cleanup
  scam_detector.features      — Feature extraction (text, company, url, …)
  scam_detector.scoring       — Rules engine, risk engine, explainability
"""

from scam_detector.pipeline import ScamDetectorPipeline
from scam_detector.scoring.explain import ScamScoreResult
from scam_detector.features import FeatureVector

__all__: list[str] = [
    "ScamDetectorPipeline",
    "ScamScoreResult",
    "FeatureVector",
]
