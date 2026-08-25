# Kaggle Internship Scam Detection Dataset Profile
**Dataset File**: `fake_internship_detection_dataset.csv`
**Profiling Date**: 2026-08-25

## 1. Dataset Shape
- **Rows (Listings)**: 1,000,000
- **Columns (Fields)**: 33

## 2. Full Column List & Data Types
| Index | Column Name | Data Type | Non-Null Count | Null Count | Null % |
|---|---|---|---|---|---|
| 1 | `posting_date` | `object` | 1,000,000 | 0 | 0.00% |
| 2 | `internship_title` | `object` | 1,000,000 | 0 | 0.00% |
| 3 | `employment_type` | `object` | 1,000,000 | 0 | 0.00% |
| 4 | `work_mode` | `object` | 1,000,000 | 0 | 0.00% |
| 5 | `industry` | `object` | 1,000,000 | 0 | 0.00% |
| 6 | `location` | `object` | 1,000,000 | 0 | 0.00% |
| 7 | `company_name` | `object` | 1,000,000 | 0 | 0.00% |
| 8 | `company_size` | `object` | 1,000,000 | 0 | 0.00% |
| 9 | `company_age` | `float64` | 990,000 | 10,000 | 1.00% |
| 10 | `linkedin_presence` | `int64` | 1,000,000 | 0 | 0.00% |
| 11 | `website_available` | `int64` | 1,000,000 | 0 | 0.00% |
| 12 | `domain_age_months` | `int64` | 1,000,000 | 0 | 0.00% |
| 13 | `verification_status` | `int64` | 1,000,000 | 0 | 0.00% |
| 14 | `stipend` | `float64` | 990,000 | 10,000 | 1.00% |
| 15 | `unrealistic_salary_flag` | `int64` | 1,000,000 | 0 | 0.00% |
| 16 | `payment_required` | `int64` | 1,000,000 | 0 | 0.00% |
| 17 | `registration_fee` | `int64` | 1,000,000 | 0 | 0.00% |
| 18 | `job_description_length` | `int64` | 1,000,000 | 0 | 0.00% |
| 19 | `grammatical_errors` | `int64` | 1,000,000 | 0 | 0.00% |
| 20 | `vague_description_score` | `int64` | 1,000,000 | 0 | 0.00% |
| 21 | `urgency_score` | `int64` | 1,000,000 | 0 | 0.00% |
| 22 | `keyword_spam_score` | `int64` | 1,000,000 | 0 | 0.00% |
| 23 | `fake_certificate_offer` | `int64` | 1,000,000 | 0 | 0.00% |
| 24 | `recruiter_experience_years` | `float64` | 1,000,000 | 0 | 0.00% |
| 25 | `recruiter_email_type` | `object` | 1,000,000 | 0 | 0.00% |
| 26 | `suspicious_email_domain` | `int64` | 1,000,000 | 0 | 0.00% |
| 27 | `recruiter_response_time_hours` | `float64` | 1,000,000 | 0 | 0.00% |
| 28 | `social_media_presence` | `int64` | 1,000,000 | 0 | 0.00% |
| 29 | `emotional_manipulation_score` | `int64` | 1,000,000 | 0 | 0.00% |
| 30 | `phishing_language_score` | `int64` | 1,000,000 | 0 | 0.00% |
| 31 | `trust_signal_score` | `float64` | 990,000 | 10,000 | 1.00% |
| 32 | `fraud_score` | `float64` | 1,000,000 | 0 | 0.00% |
| 33 | `is_fake_posting` | `int64` | 1,000,000 | 0 | 0.00% |

## 3. First 5 Rows (All Columns)
Below are the first 5 records in the dataset:

### Record 1
```json
{
  "posting_date": "2026-09-10",
  "internship_title": "ML Engineer",
  "employment_type": "Internship",
  "work_mode": "Remote",
  "industry": "Marketing",
  "location": "Berlin",
  "company_name": "Russell, Medina and Evans",
  "company_size": "Startup",
  "company_age": 23.0,
  "linkedin_presence": 1,
  "website_available": 1,
  "domain_age_months": 286,
  "verification_status": 1,
  "stipend": 43083.0,
  "unrealistic_salary_flag": 0,
  "payment_required": 0,
  "registration_fee": 0,
  "job_description_length": 2009,
  "grammatical_errors": 1,
  "vague_description_score": 42,
  "urgency_score": 14,
  "keyword_spam_score": 15,
  "fake_certificate_offer": 0,
  "recruiter_experience_years": 0.3,
  "recruiter_email_type": "Free",
  "suspicious_email_domain": 1,
  "recruiter_response_time_hours": 17.6,
  "social_media_presence": 1,
  "emotional_manipulation_score": 12,
  "phishing_language_score": 28,
  "trust_signal_score": 48.4,
  "fraud_score": 51.8,
  "is_fake_posting": 1
}
```

### Record 2
```json
{
  "posting_date": "2020-05-10",
  "internship_title": "UI/UX Designer",
  "employment_type": "Contract",
  "work_mode": "Onsite",
  "industry": "Marketing",
  "location": "Bangalore",
  "company_name": "Hays-White",
  "company_size": "Startup",
  "company_age": 12.0,
  "linkedin_presence": 0,
  "website_available": 1,
  "domain_age_months": 170,
  "verification_status": 1,
  "stipend": 26888.0,
  "unrealistic_salary_flag": 0,
  "payment_required": 0,
  "registration_fee": 0,
  "job_description_length": 1901,
  "grammatical_errors": 1,
  "vague_description_score": 51,
  "urgency_score": 29,
  "keyword_spam_score": 14,
  "fake_certificate_offer": 1,
  "recruiter_experience_years": 5.1,
  "recruiter_email_type": "Free",
  "suspicious_email_domain": 1,
  "recruiter_response_time_hours": 30.2,
  "social_media_presence": 1,
  "emotional_manipulation_score": 9,
  "phishing_language_score": 27,
  "trust_signal_score": 47.6,
  "fraud_score": 75.3,
  "is_fake_posting": 1
}
```

### Record 3
```json
{
  "posting_date": "2021-07-18",
  "internship_title": "UI/UX Designer",
  "employment_type": "Internship",
  "work_mode": "Hybrid",
  "industry": "Gaming",
  "location": "Toronto",
  "company_name": "Obrien, Gonzalez and Harris",
  "company_size": "Small",
  "company_age": 10.0,
  "linkedin_presence": 1,
  "website_available": 1,
  "domain_age_months": 130,
  "verification_status": 1,
  "stipend": 35353.0,
  "unrealistic_salary_flag": 0,
  "payment_required": 0,
  "registration_fee": 0,
  "job_description_length": 1060,
  "grammatical_errors": 0,
  "vague_description_score": 0,
  "urgency_score": 5,
  "keyword_spam_score": 26,
  "fake_certificate_offer": 0,
  "recruiter_experience_years": 6.0,
  "recruiter_email_type": "Free",
  "suspicious_email_domain": 1,
  "recruiter_response_time_hours": 12.5,
  "social_media_presence": 0,
  "emotional_manipulation_score": 26,
  "phishing_language_score": 18,
  "trust_signal_score": 98.8,
  "fraud_score": 0.0,
  "is_fake_posting": 0
}
```

### Record 4
```json
{
  "posting_date": "2021-02-04",
  "internship_title": "UI/UX Designer",
  "employment_type": "Part-Time",
  "work_mode": "Remote",
  "industry": "AI",
  "location": "Berlin",
  "company_name": "Martinez, Odonnell and Davidson",
  "company_size": "Enterprise",
  "company_age": 33.0,
  "linkedin_presence": 1,
  "website_available": 1,
  "domain_age_months": 399,
  "verification_status": 1,
  "stipend": 23666.0,
  "unrealistic_salary_flag": 0,
  "payment_required": 0,
  "registration_fee": 0,
  "job_description_length": 1523,
  "grammatical_errors": 3,
  "vague_description_score": 21,
  "urgency_score": 6,
  "keyword_spam_score": 30,
  "fake_certificate_offer": 0,
  "recruiter_experience_years": 3.8,
  "recruiter_email_type": "Corporate",
  "suspicious_email_domain": 0,
  "recruiter_response_time_hours": 24.6,
  "social_media_presence": 1,
  "emotional_manipulation_score": 20,
  "phishing_language_score": 0,
  "trust_signal_score": 72.2,
  "fraud_score": 11.0,
  "is_fake_posting": 0
}
```

### Record 5
```json
{
  "posting_date": "2020-12-31",
  "internship_title": "AI Research Intern",
  "employment_type": "Internship",
  "work_mode": "Onsite",
  "industry": "EdTech",
  "location": "Toronto",
  "company_name": "Garcia-Owens",
  "company_size": "Small",
  "company_age": 14.0,
  "linkedin_presence": 0,
  "website_available": 1,
  "domain_age_months": 172,
  "verification_status": 1,
  "stipend": 56479.0,
  "unrealistic_salary_flag": 0,
  "payment_required": 0,
  "registration_fee": 0,
  "job_description_length": 2203,
  "grammatical_errors": 3,
  "vague_description_score": 44,
  "urgency_score": 0,
  "keyword_spam_score": 19,
  "fake_certificate_offer": 0,
  "recruiter_experience_years": 7.0,
  "recruiter_email_type": "Free",
  "suspicious_email_domain": 1,
  "recruiter_response_time_hours": 30.3,
  "social_media_presence": 0,
  "emotional_manipulation_score": 16,
  "phishing_language_score": 50,
  "trust_signal_score": 34.4,
  "fraud_score": 56.0,
  "is_fake_posting": 1
}
```

## 4. Target / Label Column Identification & Class Balance
The dataset contains three fraud-related columns:
1. **`is_fake_posting`** (Primary Binary Target): `0` = Legitimate, `1` = Fake/Scam
2. **`fraud_score`** (Continuous Risk Score): Range `[0.0, 100.0]`
3. **`fake_certificate_offer`** (Specific Scam Sub-Type): `0` = No, `1` = Offer fake certificates

### Class Balance for Primary Target (`is_fake_posting`):
| Class Label | Description | Count | Percentage |
|---|---|---|---|
| `0` | Legitimate Posting | 778,042 | 77.80% |
| `1` | Fake / Scam Posting | 221,958 | 22.20% |

- **`fraud_score` distribution for `is_fake_posting == 0`**: Min = 0.00, Max = 50.00, Mean = 25.29
- **`fraud_score` distribution for `is_fake_posting == 1`**: Min = 50.00, Max = 100.00, Mean = 64.57

## 5. Null / Missing Value Rate
| Column Name | Missing Count | Missing Percentage |
|---|---|---|
| `company_age` | 10,000 | 1.00% |
| `stipend` | 10,000 | 1.00% |
| `trust_signal_score` | 10,000 | 1.00% |

## 6. Free-Text Columns Analysis
> **CRITICAL FINDING**: The Kaggle dataset **does NOT contain raw free-text fields** (such as full job descriptions, summaries, or responsibility lists).
Instead, text features have been pre-engineered/extracted into numerical score indicators:
- `job_description_length` (character length)
- `grammatical_errors` (count)
- `vague_description_score` (0–100 score)
- `urgency_score` (0–100 score)
- `keyword_spam_score` (0–100 score)
- `emotional_manipulation_score` (0–100 score)
- `phishing_language_score` (0–100 score)

### Text Score Comparison by Class (`is_fake_posting`):
| Feature Name | Overall Mean | Legitimate (`0`) Mean | Fake (`1`) Mean | Difference |
|---|---|---|---|---|
| `job_description_length` | 1799.54 | 1799.71 | 1798.95 | -0.76 |
| `grammatical_errors` | 3.00 | 2.90 | 3.36 | +0.46 |
| `vague_description_score` | 30.13 | 27.69 | 38.69 | +11.00 |
| `urgency_score` | 40.05 | 38.26 | 46.31 | +8.04 |
| `keyword_spam_score` | 25.57 | 24.51 | 29.31 | +4.80 |
| `emotional_manipulation_score` | 25.56 | 25.57 | 25.55 | -0.02 |
| `phishing_language_score` | 20.75 | 18.39 | 29.03 | +10.65 |

## 7. Structural, Numeric, and Categorical Feature Distributions
### A. Categorical & Discrete Features
#### `employment_type` Top Value Counts & Fraud Rate:
| Category | Count | % of Total | Fraud Rate (`is_fake_posting=1`) |
|---|---|---|---|
| `Part-Time` | 250,700 | 25.07% | 22.23% |
| `Internship` | 249,998 | 25.00% | 22.19% |
| `Contract` | 249,669 | 24.97% | 22.13% |
| `Full-Time` | 249,633 | 24.96% | 22.23% |

#### `work_mode` Top Value Counts & Fraud Rate:
| Category | Count | % of Total | Fraud Rate (`is_fake_posting=1`) |
|---|---|---|---|
| `Remote` | 549,339 | 54.93% | 24.41% |
| `Hybrid` | 250,526 | 25.05% | 19.45% |
| `Onsite` | 200,135 | 20.01% | 19.57% |

#### `industry` Top Value Counts & Fraud Rate:
| Category | Count | % of Total | Fraud Rate (`is_fake_posting=1`) |
|---|---|---|---|
| `AI` | 111,803 | 11.18% | 22.25% |
| `EdTech` | 111,417 | 11.14% | 22.20% |
| `Healthcare` | 111,357 | 11.14% | 22.23% |
| `FinTech` | 111,025 | 11.10% | 22.34% |
| `E-Commerce` | 111,016 | 11.10% | 22.10% |
| `Marketing` | 111,005 | 11.10% | 22.15% |
| `Gaming` | 110,967 | 11.10% | 22.12% |
| `Cybersecurity` | 110,878 | 11.09% | 22.21% |
| `Software` | 110,532 | 11.05% | 22.17% |

#### `location` Top Value Counts & Fraud Rate:
| Category | Count | % of Total | Fraud Rate (`is_fake_posting=1`) |
|---|---|---|---|
| `Sydney` | 111,520 | 11.15% | 22.08% |
| `Toronto` | 111,477 | 11.15% | 21.92% |
| `Bangalore` | 111,441 | 11.14% | 22.57% |
| `San Francisco` | 111,390 | 11.14% | 22.20% |
| `Berlin` | 110,990 | 11.10% | 22.21% |
| `Dubai` | 110,987 | 11.10% | 22.25% |
| `Singapore` | 110,882 | 11.09% | 22.22% |
| `London` | 110,754 | 11.08% | 22.10% |
| `New York` | 110,559 | 11.06% | 22.20% |

#### `company_size` Top Value Counts & Fraud Rate:
| Category | Count | % of Total | Fraud Rate (`is_fake_posting=1`) |
|---|---|---|---|
| `Small` | 300,184 | 30.02% | 22.24% |
| `Startup` | 299,863 | 29.99% | 22.24% |
| `Medium` | 249,593 | 24.96% | 22.10% |
| `Enterprise` | 150,360 | 15.04% | 22.19% |

#### `recruiter_email_type` Top Value Counts & Fraud Rate:
| Category | Count | % of Total | Fraud Rate (`is_fake_posting=1`) |
|---|---|---|---|
| `Corporate` | 749,433 | 74.94% | 16.91% |
| `Free` | 250,567 | 25.06% | 37.99% |

### B. Key Numeric Features Summary
| Feature Name | Min | Median | Mean | Max | Std Dev |
|---|---|---|---|---|---|
| `company_age` | 1.0 | 20.0 | 20.00 | 39.0 | 11.25 |
| `domain_age_months` | 1.0 | 240.0 | 239.54 | 500.0 | 135.74 |
| `stipend` | 2000.0 | 34984.0 | 35066.20 | 110428.0 | 14830.06 |
| `registration_fee` | 0.0 | 0.0 | 252.08 | 4999.0 | 881.47 |
| `recruiter_experience_years` | 0.0 | 5.0 | 5.05 | 19.6 | 2.87 |
| `recruiter_response_time_hours` | 1.0 | 18.0 | 18.18 | 63.9 | 9.61 |
| `trust_signal_score` | 0.0 | 56.9 | 56.56 | 100.0 | 16.36 |
| `fraud_score` | 0.0 | 32.3 | 34.01 | 100.0 | 21.37 |

### C. Binary Indicator Features & Fraud Rates
| Feature Name | Positive Count (`=1`) | Positive % | Fraud Rate when `=1` | Fraud Rate when `=0` |
|---|---|---|---|---|
| `linkedin_presence` | 800,764 | 80.08% | 17.91% | 39.43% |
| `website_available` | 849,597 | 84.96% | 18.88% | 40.90% |
| `verification_status` | 699,713 | 69.97% | 21.06% | 24.85% |
| `unrealistic_salary_flag` | 0 | 0.00% | nan% | 22.20% |
| `payment_required` | 99,905 | 9.99% | 68.87% | 17.02% |
| `suspicious_email_domain` | 250,567 | 25.06% | 37.99% | 16.91% |
| `social_media_presence` | 749,800 | 74.98% | 22.16% | 22.31% |
| `fake_certificate_offer` | 79,830 | 7.98% | 51.27% | 19.67% |

## 8. Schema Overlap Analysis with iFind `scam_detector`
We evaluated Kaggle dataset fields against our 22 canonical `scam_detector` schema fields:

### A. Directly or Near-Directly Equivalent Fields (5 fields)
| iFind Field | Kaggle Equivalent Column | Mapping & Conversion Notes |
|---|---|---|
| `company` | `company_name` | Direct string match (e.g. 'Smith PLC'). |
| `stipend` | `stipend` | Direct numeric amount match. |
| `datePublished` | `posting_date` | Date format string ('YYYY-MM-DD'). |
| `name` | `internship_title` | Job title (e.g. 'Marketing Intern'). |
| `city` / `country` | `location` | Location string (e.g. 'Sydney', 'Bangalore', 'San Francisco'). |

### B. iFind Schema Fields Missing in Kaggle Dataset (17 fields)
The Kaggle dataset lacks raw strings and operational metadata for the following fields:
- `_id`
- `applyLink`
- `deadlineDate`
- `state`
- `isRemote`
- `duration`
- `skills`
- `degree`
- `field`
- `experienceRequired`
- `openings`
- `summary`
- `responsibilities`
- `perks`
- `tags`
- `source`

### C. Kaggle Dataset Fields NOT in iFind Schema (28 fields)
The dataset contains specialized pre-extracted risk indicators and recruiter metadata:
- `employment_type`
- `work_mode`
- `industry`
- `company_size`
- `company_age`
- `linkedin_presence`
- `website_available`
- `domain_age_months`
- `verification_status`
- `unrealistic_salary_flag`
- `payment_required`
- `registration_fee`
- `job_description_length`
- `grammatical_errors`
- `vague_description_score`
- `urgency_score`
- `keyword_spam_score`
- `fake_certificate_offer`
- `recruiter_experience_years`
- `recruiter_email_type`
- `suspicious_email_domain`
- `recruiter_response_time_hours`
- `social_media_presence`
- `emotional_manipulation_score`
- `phishing_language_score`
- `trust_signal_score`
- `fraud_score`
- `is_fake_posting`

## 9. Data Leakage & Statistical Anomaly Analysis
We ran linear correlation and decision boundary tests across all 32 feature columns against `is_fake_posting`.

### Feature Correlation with `is_fake_posting`:
| Feature Name | Pearson Correlation coefficient | Risk Assessment |
|---|---|---|
| `fraud_score` | +0.7638 | HIGH LEAKAGE RISK / COMPOSITE TARGET |
| `payment_required` | +0.3742 | STRONG SIGNAL |
| `registration_fee` | +0.3215 | STRONG SIGNAL |
| `phishing_language_score` | +0.2785 | NORMAL |
| `vague_description_score` | +0.2431 | NORMAL |
| `suspicious_email_domain` | +0.2198 | NORMAL |
| `fake_certificate_offer` | +0.2060 | NORMAL |
| `urgency_score` | +0.1416 | NORMAL |
| `grammatical_errors` | +0.1106 | NORMAL |
| `keyword_spam_score` | +0.1102 | NORMAL |
| `recruiter_response_time_hours` | +0.0004 | NORMAL |
| `emotional_manipulation_score` | -0.0004 | NORMAL |
| `job_description_length` | -0.0005 | NORMAL |
| `stipend` | -0.0008 | NORMAL |
| `recruiter_experience_years` | -0.0015 | NORMAL |
| `social_media_presence` | -0.0015 | NORMAL |
| `domain_age_months` | -0.0294 | NORMAL |
| `company_age` | -0.0298 | NORMAL |
| `verification_status` | -0.0418 | NORMAL |
| `website_available` | -0.1894 | NORMAL |
| `linkedin_presence` | -0.2069 | NORMAL |
| `trust_signal_score` | -0.3865 | STRONG SIGNAL |
| `unrealistic_salary_flag` | +nan | NORMAL |

### Critical Data Leakage / Synthetic Artifact Findings:
1. **`fraud_score` Threshold Determinism**: `fraud_score` is a continuous composite metric $[0, 100]$. Every single posting with `fraud_score >= 50.0` (or similar exact threshold) has `is_fake_posting = 1`. `fraud_score` is the synthetic master score from which `is_fake_posting` was derived.
2. **`unrealistic_salary_flag` Constant Zero**: Column `unrealistic_salary_flag` has min=0, max=0, mean=0.0 across all 1,000,000 rows (zero variance).
3. **Perfectly Uniform Synthetic Distributions**: Company names (e.g. 'Smith PLC' repeated 1,248 times), locations, titles, and dates exhibit artificial uniform frequency, confirming synthetic generation.

## 10. Dataset Provenance
Quoted directly from the Kaggle Dataset Metadata (`aiexplorer77/internship-scam-detection-dataset`):

> **Title**: Internship Scam Detection Dataset
> **Author**: AI Explorer (`aiexplorer77`)
> **License**: MIT
> **Exact Description Quote**:
> *"This dataset presents a large-scale synthetic simulation of internship and job postings designed to model realistic recruitment behavior, phishing tactics, suspicious hiring patterns, and fraudulent employment activities across multiple industries."*
> *"The dataset combines company verification signals, recruiter behavior, compensation patterns, NLP-inspired scam indicators, and trust-related features to create realistic fraud detection scenarios suitable for machine learning, cybersecurity analytics, exploratory data analysis (EDA), and business intelligence projects."*

> **Provenance Summary**: The dataset is **100% synthetic/simulated data** generated to model fraud scenarios. It is not raw web-scraped data from real-world platforms.
