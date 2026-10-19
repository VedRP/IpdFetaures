"""
retrain.py
----------
Automated retraining pipeline for the supervised scam classifier.

This is the "self-learning" loop: instead of someone manually calling
``SupervisedScamModel.fit()`` whenever they remember to, ``run_retraining_cycle``
is meant to be invoked on a schedule (cron / CI job / admin endpoint) and:

  1. promotes any newly-qualifying applicant votes into the feedback store
     (see applicant_feedback.py) so the latest weak labels are included;
  2. refuses to run at all if there still isn't enough labeled data, or the
     labeled data is too class-imbalanced to train anything meaningful;
  3. trains a *candidate* model on a stratified training split, confidence-
     weighted exactly like a manual fit (see supervised_model.py);
  4. evaluates both the candidate and the current production model (if any)
     on the same held-out split, using ROC-AUC;
  5. only promotes the candidate to the live model path if it's at least as
     good as the incumbent (within a small configurable tolerance for
     holdout noise) — a retrain can never silently make scoring worse;
  6. versions every attempt (promoted or not) under ``versions_dir`` and
     appends one line per cycle to ``retrain_history.jsonl`` for audit and
     rollback (see ``rollback_to_version``).

This module does not run itself — nothing in this codebase calls it on a
timer yet. Wire it to a scheduler (cron, CI, an admin-triggered endpoint)
when ready; it is safe to call directly or manually in the meantime.
"""

from __future__ import annotations

import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from scam_detector.config import Config, cfg as _default_cfg
from scam_detector.feedback import FeedbackStore, build_training_labels
from scam_detector.scoring.supervised_model import SupervisedScamModel

log = logging.getLogger("scam_detector.retrain")


class RetrainResult(BaseModel):
    """Outcome of one retraining cycle — always logged, win or lose."""

    trained: bool = False
    promoted: bool = False
    reason: str = ""
    n_labeled: int = 0
    n_train: int = 0
    n_holdout: int = 0
    candidate_auc: float | None = None
    incumbent_auc: float | None = None
    model_version_path: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def _record_id_of(record: dict[str, Any], fallback_index: int) -> str:
    from scam_detector.features.duplicate_detection import _record_id
    return _record_id(record, fallback_index)


def _build_feature_matrix_for_ids(
    all_records: list[dict[str, Any]],
    record_ids: set[str],
):
    """Build (records_subset, feature_vectors_subset, feature_matrix) for
    just the given record_ids, reusing the same extractor as manual fit()."""
    from scam_detector.features import extract_all
    from scam_detector.scoring.anomaly_model import assemble_feature_matrix

    subset_records = []
    for i, r in enumerate(all_records):
        if _record_id_of(r, i) in record_ids:
            subset_records.append(r)

    feature_vectors = [extract_all(r, all_records=all_records) for r in subset_records]
    matrix = assemble_feature_matrix(subset_records, feature_vectors)
    return subset_records, feature_vectors, matrix


def _log_result(path: str | Path, result: RetrainResult) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(result.model_dump_json() + "\n")


def load_retrain_history(path: str | Path) -> list[RetrainResult]:
    p = Path(path)
    if not p.exists():
        return []
    history: list[RetrainResult] = []
    with p.open(encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                history.append(RetrainResult.model_validate_json(line))
            except Exception as exc:
                log.warning("Skipping malformed retrain history row at %s:%d (%s)", p, lineno, exc)
    return history


def run_retraining_cycle(
    all_records: list[dict[str, Any]],
    config: Config | None = None,
) -> RetrainResult:
    """
    Run one full retraining cycle and return its outcome.

    ``all_records`` must be the full current corpus of internship records
    (the same shape passed to ``pipeline.process_records``) — it's the only
    source retraining has for re-deriving features for labeled record_ids;
    there's no separate database read in this module.
    """
    cfg = config or _default_cfg
    sup_cfg = cfg.supervised

    feedback_store = FeedbackStore(cfg.feedback.store_path)

    try:
        from scam_detector.applicant_feedback import ApplicantVoteStore, promote_votes_to_feedback
        promote_votes_to_feedback(
            ApplicantVoteStore(cfg.feedback.applicant_vote_store_path), feedback_store
        )
    except Exception as exc:
        log.warning("Applicant-vote promotion skipped during retraining: %s", exc)

    history = feedback_store.load_feedback_history()
    labeled_df = build_training_labels(history)
    n_labeled = len(labeled_df)

    if n_labeled < sup_cfg.min_training_samples:
        result = RetrainResult(
            trained=False,
            reason=f"only {n_labeled} labeled samples, need {sup_cfg.min_training_samples}",
            n_labeled=n_labeled,
        )
        _log_result(sup_cfg.retrain_history_path, result)
        return result

    class_counts = labeled_df["label"].value_counts(normalize=True)
    if len(class_counts) < 2 or class_counts.min() < sup_cfg.min_class_balance:
        minority = class_counts.min() if len(class_counts) else 0.0
        result = RetrainResult(
            trained=False,
            reason=f"minority class too small ({minority:.1%} of {n_labeled} labeled rows)",
            n_labeled=n_labeled,
        )
        _log_result(sup_cfg.retrain_history_path, result)
        return result

    from sklearn.model_selection import train_test_split

    train_ids_series, holdout_ids_series = train_test_split(
        labeled_df["record_id"],
        test_size=sup_cfg.holdout_fraction,
        random_state=42,
        stratify=labeled_df["label"],
    )
    train_ids = set(train_ids_series)
    holdout_ids = set(holdout_ids_series)

    train_records, train_fvs, _ = _build_feature_matrix_for_ids(all_records, train_ids)
    train_feedback = [fb for fb in history if fb.record_id in train_ids]

    holdout_records, holdout_fvs, holdout_matrix = _build_feature_matrix_for_ids(
        all_records, holdout_ids
    )

    if holdout_matrix.empty or not train_records:
        result = RetrainResult(
            trained=False,
            reason="labeled record_ids could not be matched against all_records "
                   "(stale/missing corpus — labeled records may no longer exist in the feed)",
            n_labeled=n_labeled,
        )
        _log_result(sup_cfg.retrain_history_path, result)
        return result

    holdout_labels = labeled_df.set_index("record_id").loc[holdout_matrix.index]
    y_holdout = holdout_labels["label"].astype(int).to_numpy()
    w_holdout = holdout_labels["weight"].astype(float).to_numpy()

    if len(set(y_holdout)) < 2:
        result = RetrainResult(
            trained=False,
            reason="holdout split ended up single-class — cannot compute AUC; retry next cycle",
            n_labeled=n_labeled,
        )
        _log_result(sup_cfg.retrain_history_path, result)
        return result

    timestamp = datetime.now(timezone.utc)
    version_path = Path(sup_cfg.versions_dir) / f"supervised_model_{timestamp:%Y%m%d_%H%M%S}.joblib"

    candidate = SupervisedScamModel(
        model_path=version_path, min_training_samples=sup_cfg.min_training_samples, config=cfg
    )
    try:
        candidate.fit(
            train_records, train_fvs, train_feedback,
            min_samples=min(sup_cfg.min_training_samples, len(train_feedback)),
            autosave=False,
        )
    except Exception as exc:
        result = RetrainResult(
            trained=False,
            reason=f"candidate training failed: {exc}",
            n_labeled=n_labeled,
            n_train=len(train_records),
            n_holdout=len(holdout_records),
        )
        _log_result(sup_cfg.retrain_history_path, result)
        return result

    from sklearn.metrics import roc_auc_score

    candidate_probs = candidate.predict_proba(holdout_matrix)
    candidate_auc = float(roc_auc_score(y_holdout, candidate_probs, sample_weight=w_holdout))

    incumbent = SupervisedScamModel(model_path=sup_cfg.model_path, config=cfg)
    incumbent_auc: float | None = None
    if incumbent.load():
        try:
            incumbent_probs = incumbent.predict_proba(holdout_matrix)
            if incumbent_probs:
                incumbent_auc = float(roc_auc_score(y_holdout, incumbent_probs, sample_weight=w_holdout))
        except Exception as exc:
            log.warning("Could not evaluate incumbent model, treating as no incumbent: %s", exc)

    promote = incumbent_auc is None or candidate_auc >= incumbent_auc + sup_cfg.min_auc_improvement

    candidate.save(version_path)
    if promote:
        Path(sup_cfg.model_path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(version_path, sup_cfg.model_path)
        log.info(
            "Promoted retrained model (candidate_auc=%.4f vs incumbent_auc=%s) -> %s",
            candidate_auc, incumbent_auc, sup_cfg.model_path,
        )
    else:
        log.info(
            "Retrain candidate NOT promoted (candidate_auc=%.4f < incumbent_auc=%.4f - tolerance); kept at %s for audit only",
            candidate_auc, incumbent_auc, version_path,
        )

    result = RetrainResult(
        trained=True,
        promoted=promote,
        reason="promoted" if promote else "candidate did not beat incumbent within tolerance",
        n_labeled=n_labeled,
        n_train=len(train_records),
        n_holdout=len(holdout_records),
        candidate_auc=round(candidate_auc, 4),
        incumbent_auc=round(incumbent_auc, 4) if incumbent_auc is not None else None,
        model_version_path=str(version_path),
        timestamp=timestamp,
    )
    _log_result(sup_cfg.retrain_history_path, result)
    return result


def list_model_versions(config: Config | None = None) -> list[Path]:
    """List every retained model version artifact, oldest first."""
    cfg = config or _default_cfg
    versions_dir = Path(cfg.supervised.versions_dir)
    if not versions_dir.exists():
        return []
    return sorted(versions_dir.glob("supervised_model_*.joblib"))


def rollback_to_version(version_path: str | Path, config: Config | None = None) -> None:
    """
    Copy a previously-saved version back onto the live model path.

    Use this if a promoted retrain turns out to behave badly in practice
    despite passing its holdout check (e.g. the holdout wasn't
    representative of a newly-emerged scam pattern).
    """
    cfg = config or _default_cfg
    src = Path(version_path)
    if not src.exists():
        raise FileNotFoundError(f"Model version not found: {src}")
    dst = Path(cfg.supervised.model_path)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    log.info("Rolled back live supervised model to %s", src)
