"""
scam_detector
=============
Internship scam-detection and data-quality pipeline for iFind.

Public surface
--------------
  from scam_detector import ScamDetectorPipeline, ScamScoreResult, FeatureVector

The full pipeline is orchestrated by :mod:`scam_detector.pipeline`.
Individual stages are available under their own sub-packages:

  scam_detector.data_quality   — Phase 1 remediation / cleanup
  scam_detector.features       — Feature extraction (text, company, url, …)
  scam_detector.scoring        — Rules engine, risk engine, and explainability
"""

from scam_detector.pipeline import ScamDetectorPipeline
from scam_detector.scoring.explain import ScamScoreResult
from scam_detector.features import FeatureVector

__all__ = [
    "ScamDetectorPipeline",
    "ScamScoreResult",
    "FeatureVector",
]
