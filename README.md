# IpdFeatures

This repository contains two core components of the iFind internship platform:

## internScraper
Multi-source internship scraper (Internshala, GitHub, Indeed, Naukri, etc.)
with a moderation pipeline, Flask API, and Dockerfile for deployment.

## scam_detector
Python package implementing the internship scam-detection pipeline.
Stages: data quality remediation → feature extraction (text, company, URL,
stipend, temporal, structural, duplicate detection) → deterministic rules
engine → ML risk engine → explainability output.

### Quick start
```bash
cd scam_detector
pip install -e ".[dev]"
pytest tests/
```
