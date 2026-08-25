# iFind Platform & Scraper / Scam Detector Engine

Comprehensive backend services and ML pipelines powering **iFind**: internship scraping, data quality remediation, multi-stage scam detection, and AI resume extraction.

---

## 🏗 System Architecture & Services

```
                                  iFind Ecosystem
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
 🌐 Scraper Service             🛡 Scam Detector              📄 Resume Extractor
  (FastAPI + Selenium)           (Rules + Anomaly ML)          (pdfplumber + spaCy + CRF)
  - Scrapes 7+ platforms         - Data Quality Remediation    - Layout-aware PDF/DOCX
  - Normalizes JSON schema       - 7 Deterministic Rules       - NER & Skill Taxonomy
  - Stores in MongoDB            - IsolationForest & Risk Blend- Auto Project Link Match
```

---

## 🔍 1. iFind Scraper API

FastAPI service that orchestrates background scraping jobs across platforms (`github`, `internshala`, `indeed`, `naukri`, `unstop`, `freshersworld`, `letsintern`) and pushes clean records into MongoDB.

### Scraper Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness and health check |
| `POST` | `/scrape` | Trigger asynchronous scraping job (returns `job_id`) |
| `GET` | `/scrape/{job_id}` | Poll job status, progress, and record counts |
| `GET` | `/scrape` | List all past and active scraping jobs |
| `GET` | `/docs` | Interactive Swagger API documentation |

---

## 🛡 2. Scam Detector Pipeline (`scam_detector`)

Multi-stage fraud mitigation and data-quality engine protecting users from fake listings, advance fees, upfront credential harvesting, and shell company recruiters.

### Pipeline Stages
1. **Data Quality Remediation**: Cleans scraper category leaks, default degree fallbacks, missing deadlines (`data_quality/remediate.py`).
2. **Corpus Indexing**: Builds SBERT `DuplicateIndex` (or Jaccard fallback), peer groups, and recruiter posting velocity tables.
3. **Feature Extraction**: Computes Text, Company, URL, Stipend, Temporal, and Structural feature vectors.
4. **Unsupervised Anomaly Model**: Fits IsolationForest across a 47-column numeric feature matrix (`scoring/anomaly_model.py`).
5. **Deterministic Rules Engine**: Evaluates 7 business rules combined via Noisy-OR logic ($1 - \prod (1 - w_i)$):
   - `HardDisqualifyingSignalsRule` (weight: 0.95 — upfront payment / Aadhaar / bank requests)
   - `CrossCompanyDuplicateRule` (weight: 0.80 — duplicate listings under different companies)
   - `TyposquatDomainRule` (weight: 0.70 — domain mismatch on off-platform link)
   - `ExtremeStipendOutlierRule` (weight: 0.45 — $\|z\| > 3.0$ vs peer group)
   - `MassOpeningsVagueRoleRule` (weight: 0.40 — openings $z > 2.0$ & genericity $> 0.65$)
   - `StipendPerkContradictionRule` (weight: 0.35 — text vs stipend contradiction)
   - `UnverifiableCompanyRule` (weight: 0.10 — category leak flag)
6. **Risk Engine & Calibration**: Blends Rules ($60\%$), Anomaly ($40\%$), and optional Supervised models ($0\%$), applies Isotonic score calibration, computes confidence, and enforces decision thresholds (`clear` $< 30$, `review` $30\text{--}70$, `block` $\ge 70$).
7. **Human Review Feedback Store**: Append-only JSONL feedback store (`feedback.py`) for reviewer labeling and supervised model retraining.

### CLI & Batch Usage
```bash
# Run tests
pytest scam_detector/tests/ -v

# Run batch scoring on raw scraped JSON
python -m scam_detector.pipeline input.json output.json --sample 50
```

---

## 📄 3. Resume Extractor API (`resume-extract`)

High-precision resume parser converting PDF and DOCX files into structured JSON matching candidate resume schemas.

### Key Features & Technology Stack
- **Layout-Aware PDF Extraction**: `pdfplumber` with two-column gutter detection.
- **spaCy NER**: `en_core_web_sm` for Name (PERSON), Organization (ORG), and Location (GPE) extraction.
- **Skill Taxonomy**: `SkillNer` (ESCO ontology, ~6,000 terms) with `SKILL_FIELDS` categorization fallback.
- **CRF Sequence Labeller**: Sequence tagging for headers and experience lines (`crf_model.pkl`).
- **Project Hyperlink Auto-Matching**: Auto-associates GitHub, GitLab, and live demo links with extracted projects.
- **Publications & Interests**: Structured parsers for publication URLs and interest topics.

### Resume Extractor Endpoints
| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Service liveness check |
| `GET` | `/health` | Model status check (`spacy_ner`, `skillner`, `crf_sequence_labeller`) |
| `GET` | `/schema` | Returns Resume JSON response schema |
| `POST` | `/extract` | Upload PDF/DOCX file $\rightarrow$ returns structured Resume JSON |

---

## 📊 4. Dataset Profiling & Research

- **Kaggle Dataset Profile**: [`kaggle_internship_dataset_profile.md`](kaggle_internship_dataset_profile.md) contains full profiling, schema overlap analysis, and data leakage findings for 1,000,000 simulated listings (`aiexplorer77/internship-scam-detection-dataset`).

---

## ⚙️ Environment Variables & Secrets

Set these environment variables or HuggingFace Space Secrets:

| Secret / Env Var | Description |
|---|---|
| `MONGODB_URI` | Connection string for MongoDB Atlas database |
| `COHERE_API_KEY` | API key for Cohere AI enrichment in scrapers |

---

## 📜 License & Provenance
Developed for **iFind**. All rights reserved.

