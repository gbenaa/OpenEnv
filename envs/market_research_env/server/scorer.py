"""Reward scoring for the market-research environment."""

from __future__ import annotations

from collections import Counter
from typing import Sequence
from urllib.parse import urlparse

from market_research_env.models import EvidenceRecord


RELEVANT_TYPES = {
    "product",
    "price",
    "review",
    "risk",
    "competitor",
    "affiliate",
    "compliance",
}


def _normalise_text(value: str) -> str:
    """Normalise short text values for duplicate checks."""
    return " ".join((value or "").lower().split())


def _normalise_source_url(value: str) -> str:
    """Normalise source URLs enough for controlled local-web duplicate checks."""
    parsed = urlparse(value or "")
    if not parsed.scheme:
        return value or ""
    return parsed.path or "/"


class MarketResearchScorer:
    """Simple deterministic reward model for the first prototype."""

    def score_capture(self, record: EvidenceRecord) -> tuple[float, dict]:
        score = 0.0
        reasons: list[str] = []

        if record.claim.strip():
            score += 0.5
            reasons.append("claim_present")

        if record.source_url:
            score += 0.5
            reasons.append("source_url_present")

        if record.claim_type in RELEVANT_TYPES:
            score += 1.0
            reasons.append("relevant_claim_type")

        if record.rationale.strip():
            score += 0.5
            reasons.append("rationale_present")

        return score, {"event": "capture", "reasons": reasons}

    def score_accept(self, record: EvidenceRecord) -> tuple[float, dict]:
        score = 0.0
        reasons: list[str] = []

        text = " ".join(
            [
                record.claim.lower(),
                record.rationale.lower(),
                record.freshness.lower(),
                record.reliability.lower(),
                record.compliance_notes.lower(),
                record.source_url.lower(),
            ]
        )

        if record.claim_type in {"product", "price", "review", "risk", "competitor", "affiliate", "compliance"}:
            score += 2.0
            reasons.append("accepted_relevant_evidence")

        if "stale" in text or "2022" in text or "archive" in text:
            score -= 3.0
            reasons.append("accepted_stale_or_archived_evidence")

        if "unsupported" in text or "misleading" in text or "no tests" in text:
            score -= 3.0
            reasons.append("accepted_unsupported_or_misleading_claim")

        if record.source_url:
            score += 1.0
            reasons.append("provenance_preserved")

        return score, {"event": "accept", "reasons": reasons}

    def score_reject(self, record: EvidenceRecord) -> tuple[float, dict]:
        text = " ".join(
            [
                record.claim.lower(),
                record.rationale.lower(),
                record.rejection_reason.lower(),
                record.extracted_text_excerpt.lower(),
                record.source_url.lower(),
            ]
        )

        reasons: list[str] = []
        score = 0.5

        if "stale" in text or "archive" in text or "2022" in text:
            score += 2.0
            reasons.append("correctly_rejected_stale_evidence")

        if "unsupported" in text or "misleading" in text or "no tests" in text:
            score += 2.0
            reasons.append("correctly_rejected_unsupported_claim")

        if record.rejection_reason.strip():
            score += 1.0
            reasons.append("rejection_reason_present")

        return score, {"event": "reject", "reasons": reasons}

    def duplicate_accepted_count(self, records: Sequence[EvidenceRecord]) -> int:
        """Count extra duplicate accepted-evidence records.

        A duplicate is currently defined as the same normalised claim from the same
        source path. The first occurrence is allowed. Extra occurrences are counted.
        """

        signatures = [
            (_normalise_text(record.claim), _normalise_source_url(record.source_url))
            for record in records
            if record.claim and record.source_url
        ]
        counts = Counter(signatures)
        return sum(count - 1 for count in counts.values() if count > 1)

    def weak_accepted_count(self, records: Sequence[EvidenceRecord]) -> int:
        """Count accepted records that are too weak to deserve full bundle credit."""

        weak = 0
        for record in records:
            if not record.claim.strip():
                weak += 1
                continue
            if not record.source_url.strip():
                weak += 1
                continue
            if not record.rationale.strip():
                weak += 1
                continue
        return weak

    def score_submit(
        self,
        accepted_count: int,
        rejected_count: int,
        has_affiliate_awareness: bool,
        minimum_accepted: int,
        minimum_rejected: int,
        disallowed_visit_count: int,
        accepted_records: Sequence[EvidenceRecord] | None = None,
    ) -> tuple[float, bool, dict]:
        score = 0.0
        reasons: list[str] = []

        accepted_ok = accepted_count >= minimum_accepted
        rejected_ok = rejected_count >= minimum_rejected

        if accepted_ok:
            score += 5.0
            reasons.append("accepted_evidence_threshold_met")
        else:
            score -= 2.0
            reasons.append("accepted_evidence_threshold_not_met")

        if rejected_ok:
            score += 3.0
            reasons.append("rejected_evidence_threshold_met")
        else:
            score -= 2.0
            reasons.append("rejected_evidence_threshold_not_met")

        if has_affiliate_awareness:
            score += 2.0
            reasons.append("affiliate_disclosure_awareness_present")
        else:
            score -= 5.0
            reasons.append("affiliate_disclosure_awareness_missing")

        if disallowed_visit_count:
            score -= 5.0 * disallowed_visit_count
            reasons.append("disallowed_external_url_visit")

        duplicate_count = 0
        weak_count = 0
        if accepted_records is not None:
            duplicate_count = self.duplicate_accepted_count(accepted_records)
            weak_count = self.weak_accepted_count(accepted_records)

            if duplicate_count:
                score -= 2.0 * duplicate_count
                reasons.append("duplicate_accepted_evidence")

            if weak_count:
                score -= 1.0 * weak_count
                reasons.append("weak_accepted_evidence")

        success = (
            accepted_ok
            and rejected_ok
            and has_affiliate_awareness
            and disallowed_visit_count == 0
            and duplicate_count == 0
            and weak_count == 0
        )
        return score, success, {
            "event": "submit",
            "success": success,
            "reasons": reasons,
            "duplicate_accepted_count": duplicate_count,
            "weak_accepted_count": weak_count,
        }
