"""
scam_detector
=============
Internship scam-detection and data-quality pipeline for iFind.

<<<<<<< HEAD
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
=======
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

from scam_detector.pipeline import ScamDetectorPipeline, run_pipeline, process_records
from scam_detector.scoring.explain import ScamScoreResult
from scam_detector.features import FeatureVector
from scam_detector.feedback import (
    ReviewFeedback,
    FeedbackStore,
    build_training_labels,
)

__all__: list[str] = [
    "ScamDetectorPipeline",
    "ScamScoreResult",
    "FeatureVector",
    "run_pipeline",
    "process_records",
    "ReviewFeedback",
    "FeedbackStore",
    "build_training_labels",
>>>>>>> 7a99c785c15cfc524d32a9d883ac9d5bcdc31702
]
