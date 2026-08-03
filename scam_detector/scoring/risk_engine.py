"""
risk_engine.py
--------------
ML-based risk scoring layer (complements the deterministic rules engine).

Planned approach (to be implemented):
  - Load a trained scikit-learn or ONNX model from models/
  - Serialise FeatureVector into a flat numpy array
  - Return a calibrated probability (0.0 = safe, 1.0 = certain scam)
  - Gracefully degrade to 0.5 (neutral) when no model file is present
    or when cfg.flags.enable_ml_risk_engine is False

Model artifacts live in scam_detector/models/ and are gitignored.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class RiskEngineResult(BaseModel):
    """Output from the ML risk engine."""

    score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Calibrated scam probability from the ML model",
    )
    model_version: str = Field(default="none", description="Identifier of the loaded model")
    model_available: bool = Field(
        default=False,
        description="False when no trained model is present — score defaults to neutral 0.5",
    )


def apply_risk_engine(features: object) -> RiskEngineResult:  # features: FeatureVector
    """
    Run the ML risk model against *features*.

    Logic to be implemented — currently returns a neutral (no-model) skeleton.
    """
    # TODO: load model from models/, vectorise features, return probability
    return RiskEngineResult()
