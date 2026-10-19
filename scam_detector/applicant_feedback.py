"""
applicant_feedback.py
----------------------
Weak-label feedback loop sourced from applicants, not moderators.

The only question ever asked of an applicant is binary and post-hoc:
"Was this internship a scam? yes / no" — asked when they return to the
site, with no guarantee they ever apply, return, or answer. This signal is:

  - delayed      : arrives long after the listing was originally scored
  - sparse       : most listings will get zero responses, ever
  - selection-biased : people who feel scammed are more motivated to
                        answer than people who had an unremarkable,
                        legitimate experience
  - noisy        : one applicant's personal read, not an informed review;
                    applicants can and will mislabel (e.g. "no response"
                    isn't necessarily a scam; a real scam that paid out a
                    small stipend before vanishing might get marked "no")

This module treats it as weak supervision, never as ground truth. Raw
per-applicant votes are aggregated per internship, and a record is only
promoted into the existing moderator ``FeedbackStore`` (feedback.py) once
enough votes have accumulated AND they clearly agree one way or the other.
A single vote must never be able to flip a company's reputation or feed
the supervised model at full confidence — see ``VoteAggregate.confidence``
and the thresholds in ``promote_votes_to_feedback``.

Not wired to any frontend route. No UI calls this yet.
"""

from __future__ import annotations

import logging
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from scam_detector.feedback import FeedbackStore, ReviewFeedback

log = logging.getLogger("scam_detector.applicant_feedback")

ApplicantVoteValue = Literal["scam", "not_scam"]

# Guard rails: never let a thin or ambiguous vote set promote a record.
DEFAULT_MIN_VOTES = 3
DEFAULT_SCAM_RATIO_THRESHOLD = 0.70
DEFAULT_LEGIT_RATIO_THRESHOLD = 0.15

# Vote-volume at which confidence saturates (diminishing returns past this).
_CONFIDENCE_SCALE = 5.0


class ApplicantVote(BaseModel):
    """One applicant's post-hoc yes/no report for a single internship."""

    record_id: str = Field(description="Stable id of the internship applied to")
    applicant_id: str = Field(
        default="",
        description=(
            "Opaque applicant identifier, if available. Used only to "
            "de-duplicate repeat votes from the same applicant (a later "
            "vote overrides an earlier one); never stored or used to "
            "identify the person in any aggregate output."
        ),
    )
    vote: ApplicantVoteValue = Field(
        description=(
            "'scam' — applicant reports the internship was a scam; "
            "'not_scam' — applicant reports it was legitimate"
        )
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ApplicantVoteStore:
    """Append-only JSONL store for raw applicant votes (one line per vote)."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record_vote(self, vote: ApplicantVote | dict) -> ApplicantVote:
        event = vote if isinstance(vote, ApplicantVote) else ApplicantVote.model_validate(vote)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(event.model_dump_json() + "\n")
        log.info("Recorded applicant vote for %s -> %s", event.record_id, event.vote)
        return event

    def load_votes(self) -> list[ApplicantVote]:
        if not self.path.exists():
            return []
        votes: list[ApplicantVote] = []
        with self.path.open(encoding="utf-8") as fh:
            for lineno, raw in enumerate(fh, start=1):
                line = raw.strip()
                if not line:
                    continue
                try:
                    votes.append(ApplicantVote.model_validate_json(line))
                except Exception as exc:
                    log.warning(
                        "Skipping malformed vote at %s:%d (%s)", self.path, lineno, exc
                    )
        return votes


class VoteAggregate(BaseModel):
    """Per-record rollup of all applicant votes received so far."""

    record_id: str
    scam_votes: int = 0
    not_scam_votes: int = 0

    @property
    def total_votes(self) -> int:
        return self.scam_votes + self.not_scam_votes

    @property
    def scam_ratio(self) -> float:
        if self.total_votes == 0:
            return 0.0
        return self.scam_votes / self.total_votes

    @property
    def confidence(self) -> float:
        """
        How much weight this aggregate deserves, in (0, 1).

        Grows with vote volume with diminishing returns past roughly
        ``_CONFIDENCE_SCALE`` votes, so one report never carries the same
        weight as ten agreeing ones. 1 vote -> ~0.18, 5 votes -> ~0.63,
        10 votes -> ~0.86, 20 votes -> ~0.98.
        """
        return round(1.0 - math.exp(-self.total_votes / _CONFIDENCE_SCALE), 4)


def aggregate_votes(votes: list[ApplicantVote]) -> dict[str, VoteAggregate]:
    """
    Roll up raw votes into one :class:`VoteAggregate` per ``record_id``.

    If the same ``applicant_id`` voted on the same record more than once,
    only their most recent vote counts — people can correct an earlier
    report instead of it being double-counted.
    """
    latest_per_voter: dict[tuple[str, str], ApplicantVote] = {}
    for v in votes:
        voter_key = v.applicant_id or f"__anon__{id(v)}"
        key = (v.record_id, voter_key)
        existing = latest_per_voter.get(key)
        if existing is None or v.timestamp >= existing.timestamp:
            latest_per_voter[key] = v

    aggregates: dict[str, VoteAggregate] = {}
    for (record_id, _voter), v in latest_per_voter.items():
        agg = aggregates.setdefault(record_id, VoteAggregate(record_id=record_id))
        if v.vote == "scam":
            agg.scam_votes += 1
        else:
            agg.not_scam_votes += 1
    return aggregates


def promote_votes_to_feedback(
    vote_store: ApplicantVoteStore,
    feedback_store: FeedbackStore,
    *,
    min_votes: int = DEFAULT_MIN_VOTES,
    scam_ratio_threshold: float = DEFAULT_SCAM_RATIO_THRESHOLD,
    legit_ratio_threshold: float = DEFAULT_LEGIT_RATIO_THRESHOLD,
) -> list[ReviewFeedback]:
    """
    Turn accumulated applicant votes into ``ReviewFeedback`` entries.

    Guard rails (see module docstring):
      - a record needs >= ``min_votes`` total votes before it can be
        promoted at all — a lone report is never enough on its own.
      - ``scam_ratio >= scam_ratio_threshold`` -> promoted as
        ``confirmed_scam``.
      - ``scam_ratio <= legit_ratio_threshold`` -> promoted as
        ``confirmed_legit``.
      - anything in between is left unpromoted: genuinely disputed/
        ambiguous records should not be forced into either bucket.

    Idempotent: records already present in the ``FeedbackStore`` (by
    ``record_id``) are skipped, so repeated calls never duplicate entries
    and a late, noisy vote can never silently overwrite an existing
    moderator decision.
    """
    aggregates = aggregate_votes(vote_store.load_votes())
    already_fed_back = {fb.record_id for fb in feedback_store.load_feedback_history()}

    promoted: list[ReviewFeedback] = []
    for record_id, agg in aggregates.items():
        if record_id in already_fed_back:
            continue
        if agg.total_votes < min_votes:
            continue

        if agg.scam_ratio >= scam_ratio_threshold:
            decision: Literal["confirmed_scam", "confirmed_legit"] = "confirmed_scam"
        elif agg.scam_ratio <= legit_ratio_threshold:
            decision = "confirmed_legit"
        else:
            continue  # disputed — leave unlabeled rather than guess

        fb = ReviewFeedback(
            record_id=record_id,
            reviewer_decision=decision,
            reviewer_notes=(
                f"auto-promoted from {agg.total_votes} applicant vote(s) "
                f"({agg.scam_ratio:.0%} reported scam)"
            ),
            confidence=agg.confidence,
            source="applicant_vote_aggregate",
        )
        feedback_store.record_feedback(fb)
        promoted.append(fb)

    if promoted:
        log.info(
            "Promoted %d record(s) from applicant votes to the feedback store",
            len(promoted),
        )
    return promoted
