<<<<<<< HEAD
---
title: iFind Scraper API
emoji: 🔍
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# iFind Scraper API

FastAPI service that runs internship scrapers and pushes results through the
moderation pipeline into MongoDB.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness check |
| `POST` | `/scrape` | Start a scrape job (returns `job_id` immediately) |
| `GET` | `/scrape/{job_id}` | Poll job status |
| `GET` | `/scrape` | List all jobs |
| `GET` | `/docs` | Swagger UI |

## Environment secrets

Set these in the Space **Settings → Secrets** tab:

| Secret | Description |
|--------|-------------|
| `MONGODB_URI` | MongoDB Atlas connection string |
| `COHERE_API_KEY` | Cohere API key (used by GitHub / Indeed / Internshala scrapers for AI enrichment) |

## Usage

```bash
# Start all scrapers
curl -X POST https://<your-space>.hf.space/scrape \
  -H "Content-Type: application/json" \
  -d '{"scrapers": ["github", "internshala", "indeed", "naukri", "unstop", "freshersworld", "letsintern"]}'

# Poll for result
curl https://<your-space>.hf.space/scrape/<job_id>
```
=======
﻿# scam_detector

Internship scam-detection pipeline for iFind.

## Pipeline stages

1. Data quality remediation (`data_quality.remediate_batch`)
2. Corpus-level structures (duplicate index, peer groups, company frequency)
3. Feature extraction (text, company, URL, stipend, temporal, structural)
4. Unsupervised anomaly scoring (`AnomalyModel`)
5. Deterministic rules engine (`RulesEngine`)
6. Risk blending (`RiskEngine.score_record`)
7. Batch CLI (`python -m scam_detector.pipeline`)

Human-review feedback (`feedback.py`) is available but not wired into the main pipeline yet.

## Quick start

```bash
cd scam_detector
pip install -e ".[dev]"
pytest tests/
python -m scam_detector.pipeline input.json output.json --sample 20
```

See `AUDIT_REPORT.md` for implementation status and audit notes.
>>>>>>> 7a99c785c15cfc524d32a9d883ac9d5bcdc31702
