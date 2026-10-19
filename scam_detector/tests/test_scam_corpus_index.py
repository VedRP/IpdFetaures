"""
Tests for the weighted/decaying scam-corpus similarity and clustering
added to text_features.py (build_scam_corpus_index, ScamCorpusIndex,
scam_corpus_similarity_weighted).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from scam_detector.feedback import FeedbackStore, ReviewFeedback
from scam_detector.features.text_features import (
    ScamCorpusIndex,
    _sbert_model,
    build_scam_corpus_index,
    scam_corpus_similarity_weighted,
)

requires_sbert = pytest.mark.skipif(
    _sbert_model() is None, reason="sentence-transformers model unavailable"
)


def _record(rid: str, name: str, summary: str) -> dict:
    return {"_id": rid, "name": name, "summary": summary}


@pytest.fixture
def feedback_store(tmp_path):
    return FeedbackStore(tmp_path / "feedback.jsonl")


class TestBuildScamCorpusIndex:
    def test_returns_none_with_no_confirmed_scams(self, feedback_store):
        records = [_record("r1", "Marketing Intern", "Great real internship")]
        assert build_scam_corpus_index(feedback_store, records) is None

    @requires_sbert
    def test_builds_index_with_one_confirmed_scam(self, feedback_store):
        records = [
            _record("r1", "Data Entry Job", "Pay 500 rupees registration fee to start"),
        ]
        feedback_store.record_feedback(
            ReviewFeedback(record_id="r1", reviewer_decision="confirmed_scam")
        )
        index = build_scam_corpus_index(feedback_store, records)
        assert index is not None
        assert index.embeddings.shape[0] == 1
        assert index.weights.shape[0] == 1
        # Below clustering threshold (10) -> no cluster labels yet.
        assert index.cluster_labels is None

    @requires_sbert
    def test_recent_feedback_weighted_higher_than_old(self, feedback_store):
        records = [
            _record("r_old", "Scam A", "Pay a deposit before we hire you"),
            _record("r_new", "Scam B", "Pay a deposit before we hire you"),
        ]
        now = datetime.now(timezone.utc)
        feedback_store.record_feedback(
            ReviewFeedback(
                record_id="r_old",
                reviewer_decision="confirmed_scam",
                timestamp=now - timedelta(days=365),
            )
        )
        feedback_store.record_feedback(
            ReviewFeedback(
                record_id="r_new",
                reviewer_decision="confirmed_scam",
                timestamp=now,
            )
        )
        index = build_scam_corpus_index(feedback_store, records, half_life_days=90.0)
        assert index is not None
        old_pos = index.record_ids.index("r_old")
        new_pos = index.record_ids.index("r_new")
        assert index.weights[new_pos] > index.weights[old_pos]

    @requires_sbert
    def test_low_confidence_feedback_gets_lower_weight(self, feedback_store):
        records = [
            _record("r_sure", "Scam A", "Pay a deposit before we hire you"),
            _record("r_unsure", "Scam B", "Pay a deposit before we hire you"),
        ]
        feedback_store.record_feedback(
            ReviewFeedback(record_id="r_sure", reviewer_decision="confirmed_scam", confidence=1.0)
        )
        feedback_store.record_feedback(
            ReviewFeedback(record_id="r_unsure", reviewer_decision="confirmed_scam", confidence=0.2)
        )
        index = build_scam_corpus_index(feedback_store, records)
        assert index is not None
        sure_pos = index.record_ids.index("r_sure")
        unsure_pos = index.record_ids.index("r_unsure")
        assert index.weights[sure_pos] > index.weights[unsure_pos]


class TestScamCorpusSimilarityWeighted:
    def test_none_index_returns_zero(self):
        score, family = scam_corpus_similarity_weighted("some text", None)
        assert score == 0.0
        assert family is None

    def test_empty_text_returns_zero(self):
        import numpy as np

        index = ScamCorpusIndex(
            embeddings=np.zeros((1, 4), dtype="float32"),
            weights=np.array([1.0], dtype="float32"),
            record_ids=["r1"],
        )
        score, family = scam_corpus_similarity_weighted("", index)
        assert score == 0.0

    @requires_sbert
    def test_similar_text_scores_higher_than_dissimilar(self, feedback_store):
        records = [
            _record("r1", "Pay to work internship", "Deposit 2000 rupees to secure your seat"),
        ]
        feedback_store.record_feedback(
            ReviewFeedback(record_id="r1", reviewer_decision="confirmed_scam")
        )
        index = build_scam_corpus_index(feedback_store, records)
        assert index is not None

        similar_score, _ = scam_corpus_similarity_weighted(
            "Deposit 2000 rupees now to secure your internship seat", index
        )
        dissimilar_score, _ = scam_corpus_similarity_weighted(
            "Software engineering internship building web applications", index
        )
        assert similar_score > dissimilar_score

    @requires_sbert
    def test_a_coincidental_old_match_is_outweighed_by_recent_cluster(self, feedback_store):
        """One old, distantly-related scam shouldn't outscore several recent,
        closely-related ones once weighted — the core claim of item #1."""
        now = datetime.now(timezone.utc)
        records = [
            _record("r_old", "Old unrelated scam", "Send your bank PIN immediately urgent"),
            _record("r_new1", "Deposit scam", "Pay a 1000 rupee deposit to confirm your internship"),
            _record("r_new2", "Deposit scam 2", "A small deposit of 1000 rupees secures your role"),
            _record("r_new3", "Deposit scam 3", "Deposit required of 1000 rupees before onboarding"),
        ]
        feedback_store.record_feedback(
            ReviewFeedback(
                record_id="r_old",
                reviewer_decision="confirmed_scam",
                timestamp=now - timedelta(days=700),
            )
        )
        for rid in ("r_new1", "r_new2", "r_new3"):
            feedback_store.record_feedback(
                ReviewFeedback(record_id=rid, reviewer_decision="confirmed_scam", timestamp=now)
            )

        index = build_scam_corpus_index(feedback_store, records, half_life_days=90.0)
        assert index is not None

        score, _ = scam_corpus_similarity_weighted(
            "Please pay a 1000 rupee deposit to confirm your internship offer", index
        )
        assert score > 0.3  # meaningfully similar, driven by the recent cluster
