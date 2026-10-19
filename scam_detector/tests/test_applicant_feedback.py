"""Tests for applicant_feedback.py — the weak-label applicant vote loop."""

from __future__ import annotations

import pytest

from scam_detector.applicant_feedback import (
    ApplicantVote,
    ApplicantVoteStore,
    VoteAggregate,
    aggregate_votes,
    promote_votes_to_feedback,
)
from scam_detector.feedback import FeedbackStore


@pytest.fixture
def vote_store(tmp_path):
    return ApplicantVoteStore(tmp_path / "votes.jsonl")


@pytest.fixture
def feedback_store(tmp_path):
    return FeedbackStore(tmp_path / "feedback.jsonl")


class TestVoteAggregate:
    def test_confidence_grows_with_volume(self):
        one = VoteAggregate(record_id="r1", scam_votes=1, not_scam_votes=0)
        five = VoteAggregate(record_id="r1", scam_votes=5, not_scam_votes=0)
        twenty = VoteAggregate(record_id="r1", scam_votes=20, not_scam_votes=0)
        assert one.confidence < five.confidence < twenty.confidence
        assert twenty.confidence > 0.95

    def test_single_vote_has_low_confidence(self):
        agg = VoteAggregate(record_id="r1", scam_votes=1, not_scam_votes=0)
        assert agg.confidence < 0.25

    def test_scam_ratio(self):
        agg = VoteAggregate(record_id="r1", scam_votes=3, not_scam_votes=1)
        assert agg.scam_ratio == 0.75


class TestAggregateVotes:
    def test_aggregates_multiple_voters(self):
        votes = [
            ApplicantVote(record_id="r1", applicant_id="a1", vote="scam"),
            ApplicantVote(record_id="r1", applicant_id="a2", vote="scam"),
            ApplicantVote(record_id="r1", applicant_id="a3", vote="not_scam"),
        ]
        aggs = aggregate_votes(votes)
        assert aggs["r1"].scam_votes == 2
        assert aggs["r1"].not_scam_votes == 1

    def test_same_voter_only_counts_latest(self):
        from datetime import datetime, timedelta, timezone

        t0 = datetime.now(timezone.utc)
        votes = [
            ApplicantVote(record_id="r1", applicant_id="a1", vote="not_scam", timestamp=t0),
            ApplicantVote(
                record_id="r1", applicant_id="a1", vote="scam", timestamp=t0 + timedelta(hours=1)
            ),
        ]
        aggs = aggregate_votes(votes)
        assert aggs["r1"].scam_votes == 1
        assert aggs["r1"].not_scam_votes == 0

    def test_anonymous_votes_each_count_separately(self):
        votes = [
            ApplicantVote(record_id="r1", vote="scam"),
            ApplicantVote(record_id="r1", vote="scam"),
        ]
        aggs = aggregate_votes(votes)
        assert aggs["r1"].scam_votes == 2


class TestPromoteVotesToFeedback:
    def test_does_not_promote_below_min_votes(self, vote_store, feedback_store):
        vote_store.record_vote(ApplicantVote(record_id="r1", applicant_id="a1", vote="scam"))
        vote_store.record_vote(ApplicantVote(record_id="r1", applicant_id="a2", vote="scam"))
        promoted = promote_votes_to_feedback(vote_store, feedback_store, min_votes=3)
        assert promoted == []
        assert feedback_store.load_feedback_history() == []

    def test_promotes_confirmed_scam_on_strong_agreement(self, vote_store, feedback_store):
        for i in range(4):
            vote_store.record_vote(
                ApplicantVote(record_id="r1", applicant_id=f"a{i}", vote="scam")
            )
        promoted = promote_votes_to_feedback(vote_store, feedback_store, min_votes=3)
        assert len(promoted) == 1
        assert promoted[0].reviewer_decision == "confirmed_scam"
        assert promoted[0].source == "applicant_vote_aggregate"
        assert 0.0 < promoted[0].confidence < 1.0

    def test_promotes_confirmed_legit_on_strong_disagreement(self, vote_store, feedback_store):
        for i in range(4):
            vote_store.record_vote(
                ApplicantVote(record_id="r1", applicant_id=f"a{i}", vote="not_scam")
            )
        promoted = promote_votes_to_feedback(vote_store, feedback_store, min_votes=3)
        assert len(promoted) == 1
        assert promoted[0].reviewer_decision == "confirmed_legit"

    def test_disputed_record_is_not_promoted(self, vote_store, feedback_store):
        vote_store.record_vote(ApplicantVote(record_id="r1", applicant_id="a1", vote="scam"))
        vote_store.record_vote(ApplicantVote(record_id="r1", applicant_id="a2", vote="scam"))
        vote_store.record_vote(ApplicantVote(record_id="r1", applicant_id="a3", vote="not_scam"))
        promoted = promote_votes_to_feedback(vote_store, feedback_store, min_votes=3)
        assert promoted == []

    def test_idempotent_does_not_duplicate_or_overwrite(self, vote_store, feedback_store):
        for i in range(4):
            vote_store.record_vote(
                ApplicantVote(record_id="r1", applicant_id=f"a{i}", vote="scam")
            )
        promote_votes_to_feedback(vote_store, feedback_store, min_votes=3)
        # A late, disagreeing vote arrives after promotion.
        vote_store.record_vote(ApplicantVote(record_id="r1", applicant_id="a5", vote="not_scam"))
        promoted_again = promote_votes_to_feedback(vote_store, feedback_store, min_votes=3)
        assert promoted_again == []
        history = feedback_store.load_feedback_history()
        assert len(history) == 1
        assert history[0].reviewer_decision == "confirmed_scam"

    def test_does_not_overwrite_existing_moderator_decision(self, vote_store, feedback_store):
        from scam_detector.feedback import ReviewFeedback

        feedback_store.record_feedback(
            ReviewFeedback(record_id="r1", reviewer_decision="confirmed_legit")
        )
        for i in range(5):
            vote_store.record_vote(
                ApplicantVote(record_id="r1", applicant_id=f"a{i}", vote="scam")
            )
        promoted = promote_votes_to_feedback(vote_store, feedback_store, min_votes=3)
        assert promoted == []
        history = feedback_store.load_feedback_history()
        assert len(history) == 1
        assert history[0].reviewer_decision == "confirmed_legit"
