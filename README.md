# scam_detector

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
