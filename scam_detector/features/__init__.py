"""
scam_detector.features
======================
Feature extraction layer.  Each module is responsible for one domain of
signals and populates its slice of the shared :class:`FeatureVector`.

Exports
-------
  FeatureVector              — Aggregated feature vector (all domains)
  TextFeatureVector          — Detailed text-feature model (standalone use)
  CompanyUrlFeatureVector    — Combined company + URL feature vector
  extract_all                — Convenience: run every enabled extractor
  extract_text_features      — Text extractor
  extract_company_url_features — Company + URL extractor
"""

from scam_detector.features.text_features import (
    TextFeatures,
    TextFeatureVector,
    extract_text_features,
    urgency_score,
    caps_and_punctuation_ratio,
    genericity_score,
    title_summary_alignment,
    readability_and_grammar_signals,
    sensitive_info_request_detector,
    boilerplate_similarity,
)
from scam_detector.features.company_features import (
    CompanyFeatures,
    CompanyUrlFeatureVector,
    extract_company_url_features,
    is_company_suspect,
    has_legal_suffix,
    company_posting_frequency,
    typosquat_brand_distance,
)
from scam_detector.features.url_features import (
    UrlFeatures,
    parse_url_components,
    is_platform_internal_link,
    url_entropy,
    is_url_shortener,
    domain_company_name_similarity,
    is_known_ats_domain,
)
from scam_detector.features.stipend_features import StipendFeatures
from scam_detector.features.temporal_features import TemporalFeatures
from scam_detector.features.structural_features import StructuralFeatures
from scam_detector.features.duplicate_detection import (
    DuplicateIndex,
    DuplicateMatch,
    ClusterReport,
    cross_company_duplicate_flag,
)

from pydantic import BaseModel, Field


class FeatureVector(BaseModel):
    """
    Aggregated feature vector produced by all extractors.
    Passed directly into the scoring layer.
    """

    text: TextFeatureVector = Field(default_factory=TextFeatureVector)
    company: CompanyFeatures = Field(default_factory=CompanyFeatures)
    url: UrlFeatures = Field(default_factory=UrlFeatures)
    stipend: StipendFeatures = Field(default_factory=StipendFeatures)
    temporal: TemporalFeatures = Field(default_factory=TemporalFeatures)
    structural: StructuralFeatures = Field(default_factory=StructuralFeatures)


def extract_all(
    record: object,
    all_records: list | None = None,
) -> FeatureVector:
    """
    Run all feature extractors against a remediated record and return a
    unified :class:`FeatureVector`.

    Text and company/URL extractors are fully implemented.
    Other extractors (stipend, temporal, structural) remain stubs.
    """
    raw: dict = record.record if hasattr(record, "record") else record  # type: ignore[union-attr]
    flags: dict = record.flags if hasattr(record, "flags") else {}      # type: ignore[union-attr]

    raw_with_flags = {**raw, "_flags": flags}
    batch = all_records or [raw]

    cu = extract_company_url_features(raw_with_flags, all_records=batch, flags=flags)

    return FeatureVector(
        text=extract_text_features(raw_with_flags),
        company=cu.company,
        url=cu.url,
    )


__all__: list[str] = [
    "FeatureVector",
    "TextFeatureVector",
    "TextFeatures",
    "CompanyFeatures",
    "UrlFeatures",
    "CompanyUrlFeatureVector",
    "StipendFeatures",
    "TemporalFeatures",
    "StructuralFeatures",
    "extract_all",
    "extract_text_features",
    "extract_company_url_features",
    "is_company_suspect",
    "has_legal_suffix",
    "company_posting_frequency",
    "typosquat_brand_distance",
    "parse_url_components",
    "is_platform_internal_link",
    "url_entropy",
    "is_url_shortener",
    "domain_company_name_similarity",
    "is_known_ats_domain",
    "DuplicateIndex",
    "DuplicateMatch",
    "ClusterReport",
    "cross_company_duplicate_flag",
    "urgency_score",
    "caps_and_punctuation_ratio",
    "genericity_score",
    "title_summary_alignment",
    "readability_and_grammar_signals",
    "sensitive_info_request_detector",
    "boilerplate_similarity",
]
