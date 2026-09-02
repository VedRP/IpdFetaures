"""
test_api.py
-----------
Tests for the scam_detector FastAPI endpoints.
"""

from __future__ import annotations

import pytest
from scam_detector.api import _FASTAPI_AVAILABLE, create_app

if _FASTAPI_AVAILABLE:
    from fastapi.testclient import TestClient


@pytest.mark.skipif(not _FASTAPI_AVAILABLE, reason="FastAPI is not installed")
def test_api_health() -> None:
    app = create_app()
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "shap_available" in data
    assert "decision_thresholds" in data


@pytest.mark.skipif(not _FASTAPI_AVAILABLE, reason="FastAPI is not installed")
def test_api_score_single() -> None:
    app = create_app()
    client = TestClient(app)
    payload = {
        "title": "Software Engineering Intern",
        "company": "Google",
        "applyLink": "https://careers.google.com/jobs/123",
        "stipend": {"amount": 50000, "period": "monthly"},
        "summary": "Join our engineering team to build scalable systems.",
    }
    response = client.post("/score", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "scam_score" in data
    assert "decision" in data
    assert data["decision"] in ("clear", "review", "block")


@pytest.mark.skipif(not _FASTAPI_AVAILABLE, reason="FastAPI is not installed")
def test_api_score_batch() -> None:
    app = create_app()
    client = TestClient(app)
    payload = {
        "records": [
            {
                "_id": "rec_1",
                "name": "Backend Intern",
                "company": "Company A",
                "applyLink": "https://company-a.com/apply",
                "summary": "Develop python APIs",
            },
            {
                "_id": "rec_2",
                "name": "Frontend Intern",
                "company": "Company B",
                "applyLink": "https://company-b.com/apply",
                "summary": "Develop React components",
            },
        ]
    }
    response = client.post("/score/batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] == 2
    assert "results" in data


@pytest.mark.skipif(not _FASTAPI_AVAILABLE, reason="FastAPI is not installed")
def test_api_graph_analyze() -> None:
    app = create_app()
    client = TestClient(app)
    payload = {
        "records": [
            {"company": "Org 1", "applyLink": "https://sharedinfra.xyz/apply"},
            {"company": "Org 2", "applyLink": "https://sharedinfra.xyz/apply"},
            {"company": "Org 3", "applyLink": "https://sharedinfra.xyz/apply"},
            {"company": "Org 4", "applyLink": "https://sharedinfra.xyz/apply"},
        ],
        "target_company": "Org 1",
    }
    response = client.post("/graph/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert data["metrics"]["multi_company_networks_count"] == 1
    assert data["target_company_profile"]["shared_infrastructure"] is True
