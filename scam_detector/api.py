"""
api.py
------
FastAPI production REST API for the iFind Scam Detection Engine.

Endpoints:
  - GET  /health          -> Status, version, and component availability
  - POST /score           -> Score a single internship listing
  - POST /score/batch     -> Batch-score a list of listings with cross-record graph/duplicate detection
  - POST /graph/analyze   -> Network topological metrics and coordinated cluster analysis
  - POST /explain         -> Human review report rendering and feature attribution breakdown
"""

from __future__ import annotations

import logging
from typing import Any, Optional
from pydantic import BaseModel, Field

try:
    from fastapi import FastAPI, HTTPException, status
    from fastapi.middleware.cors import CORSMiddleware
    _FASTAPI_AVAILABLE = True
except ImportError:
    _FASTAPI_AVAILABLE = False

from scam_detector.config import cfg
from scam_detector.pipeline import score_batch, score_record
from scam_detector.scoring.explain import render_explanation, ScamScoreResult
from scam_detector.features.graph_features import (
    build_company_infrastructure_graph,
    compute_graph_network_metrics,
    company_network_risk_profile,
)

log = logging.getLogger("scam_detector.api")


# ---------------------------------------------------------------------------
# Pydantic Request / Response Models
# ---------------------------------------------------------------------------


class InternshipInput(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    title: Optional[str] = Field(default=None, alias="name")
    company: Optional[str] = None
    applyLink: Optional[str] = Field(default=None, alias="apply_link")
    summary: Optional[str] = None
    description: Optional[str] = None
    stipend: Optional[Any] = None
    duration: Optional[Any] = None
    location: Optional[Any] = None
    skills: Optional[list[str]] = None
    openings: Optional[int] = None
    source: Optional[str] = "api"


class ScoreBatchRequest(BaseModel):
    records: list[dict[str, Any]] = Field(..., min_length=1)


class ScoreResponse(BaseModel):
    id: str
    company: str
    scam_score: float
    decision: str
    confidence: float
    confidence_level: str
    explanation_summary: str
    triggered_rules: list[str]
    top_contributing_features: list[tuple[str, float]]
    shared_infrastructure: bool
    duplicate_cluster_network_size: int
    report: Optional[str] = None


class BatchScoreResponse(BaseModel):
    total_records: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    results: list[dict[str, Any]]


class GraphAnalyzeRequest(BaseModel):
    records: list[dict[str, Any]] = Field(..., min_length=1)
    target_company: Optional[str] = None


class GraphAnalyzeResponse(BaseModel):
    metrics: dict[str, Any]
    target_company_profile: Optional[dict[str, Any]] = None


# ---------------------------------------------------------------------------
# FastAPI App Factory
# ---------------------------------------------------------------------------


def create_app() -> Any:
    if not _FASTAPI_AVAILABLE:
        raise RuntimeError("FastAPI is not installed. Install with: pip install fastapi uvicorn")

    app = FastAPI(
        title="iFind Scam Detection API",
        version="0.1.0",
        description="ML + Deterministic Rules + Graph Infrastructure Scam Detection Engine",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health_check() -> dict[str, Any]:
        from scam_detector.scoring.anomaly_model import _SHAP_AVAILABLE
        return {
            "status": "healthy",
            "version": "0.1.0",
            "shap_available": _SHAP_AVAILABLE,
            "enable_shap_explanations": cfg.flags.enable_shap_anomaly_explanations,
            "decision_thresholds": {
                "clear_below": cfg.decision_thresholds.clear_below,
                "block_at_or_above": cfg.decision_thresholds.block_at_or_above,
            },
        }

    @app.post("/score", response_model=ScoreResponse)
    def score_single(item: InternshipInput) -> ScoreResponse:
        try:
            raw_dict = item.model_dump(by_alias=True, exclude_none=True)
            batch_res = score_batch([raw_dict])
            if not batch_res:
                raise HTTPException(status_code=500, detail="Scoring engine returned empty result")
            scored = batch_res[0]
            rid = str(scored.get("_id") or scored.get("id") or "item_0")
            co = str(scored.get("company") or "Unknown")
            
            return ScoreResponse(
                id=rid,
                company=co,
                scam_score=float(scored.get("scam_score", 0.0)),
                decision=str(scored.get("decision", "clear")),
                confidence=float(scored.get("confidence", 1.0)),
                confidence_level="high" if scored.get("confidence", 1.0) >= 0.7 else ("medium" if scored.get("confidence", 1.0) >= 0.4 else "low"),
                explanation_summary=str(scored.get("explanation_summary", "")),
                triggered_rules=list(scored.get("triggered_rules", [])),
                top_contributing_features=[],
                shared_infrastructure=bool(scored.get("shared_infrastructure", False)),
                duplicate_cluster_network_size=int(scored.get("duplicate_cluster_network_size", 1)),
            )
        except Exception as exc:
            log.exception("Error scoring record: %s", exc)
            raise HTTPException(status_code=500, detail=str(exc))

    @app.post("/score/batch", response_model=BatchScoreResponse)
    def score_batch_endpoint(req: ScoreBatchRequest) -> BatchScoreResponse:
        try:
            scored_records = score_batch(req.records)
            high_count = sum(1 for r in scored_records if r.get("decision") == "block")
            med_count = sum(1 for r in scored_records if r.get("decision") == "review")
            low_count = sum(1 for r in scored_records if r.get("decision") == "clear")

            return BatchScoreResponse(
                total_records=len(scored_records),
                high_risk_count=high_count,
                medium_risk_count=med_count,
                low_risk_count=low_count,
                results=scored_records,
            )
        except Exception as exc:
            log.exception("Error scoring batch: %s", exc)
            raise HTTPException(status_code=500, detail=str(exc))

    @app.post("/graph/analyze", response_model=GraphAnalyzeResponse)
    def analyze_graph_endpoint(req: GraphAnalyzeRequest) -> GraphAnalyzeResponse:
        try:
            graph = build_company_infrastructure_graph(req.records)
            metrics = compute_graph_network_metrics(graph)
            
            profile = None
            if req.target_company:
                profile = company_network_risk_profile(req.target_company, graph)

            return GraphAnalyzeResponse(
                metrics=metrics,
                target_company_profile=profile,
            )
        except Exception as exc:
            log.exception("Error analyzing graph: %s", exc)
            raise HTTPException(status_code=500, detail=str(exc))

    return app


# Module-level default application instance
if _FASTAPI_AVAILABLE:
    app = create_app()
else:
    app = None
