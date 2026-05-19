"""Reward scoring for the market-research environment."""

from __future__ import annotations

from collections import Counter
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

SOURCE_TYPE_WEIGHTS = {
    "controlled_local_page": 0.5,
    "manual_snapshot": 0.5,
    "cached_page": 0.25,
    "archived_page": -1.0,
    "unknown": -0.25,
}

ACCEPTED_FRESHNESS_WEIGHTS = {
    "current": 0.75,
    "recent": 0.5,
    "stale": -3.0,
    "archived": -3.0,
    "unknown": -0.25,
}

REJECTED_FRESHNESS_REWARDS = {
    "stale": 1.0,
    "archived": 1.0,
}

RELIABILITY_WEIGHTS = {
    "controlled_local_page": 0.5,
    "supported": 0.5,
    "unknown": 0.0,
    "unsupported": -1.0,
}


class MarketResearchScorer:
    """Deterministic reward model for the first prototype.

    The scorer is intentionally simple. It is designed to make desirable
    research behaviour visible and testable before live commercial sources are
    introduced.
    """

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

        if record.claim_type in RELEVANT_TYPES:
            score += 2.0
            reasons.append("accepted_relevant_evidence")

        if record.source_url:
            score += 1.0
            reasons.append("provenance_preserved")

        source_weight = SOURCE_TYPE_WEIGHTS.get(record.source_type, SOURCE_TYPE_WEIGHTS["unknown"])
        if source_weight:
            score += source_weight
            reasons.append(f"source_type_{record.source_type}")

        freshness_weight = ACCEPTED_FRESHNESS_WEIGHTS.get(
            record.freshness,
            ACCEPTED_FRESHNESS_WEIGHTS["unknown"],
        )
        if freshness_weight:
            score += freshness_weight
            reasons.append(f"freshness_{record.freshness}")

        reliability_weight = RELIABILITY_WEIGHTS.get(record.reliability, 0.0)
        if reliability_weight:
            score += reliability_weight
            reasons.append(f"reliability_{record.reliability}")

        if "stale" in text or "2022" in text or "archive" in text:
            score -= 3.0
            reasons.append("accepted_stale_or_archived_evidence")

        if "unsupported" in text or "misleading" in text or "no tests" in text:
            score -= 3.0
            reasons.append("accepted_unsupported_or_misleading_claim")

        return score, {"event": "accept", "reasons": reasons}

    def score_reject(self, record: EvidenceRecord) -> tuple[float, dict]:
        text = " ".join(
            [
                record.claim.lower(),
                record.rationale.lower(),
                record.rejection_reason.lower(),
                record.extracted_text_excerpt.lower(),
                record.source_url.lower(),
                record.freshness.lower(),
                record.reliability.lower(),
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

        freshness_reward = REJECTED_FRESHNESS_REWARDS.get(record.freshness, 0.0)
        if freshness_reward:
            score += freshness_reward
            reasons.append(f"rejected_freshness_{record.freshness}")

        if record.reliability == "unsupported":
            score += 1.0
            reasons.append("rejected_unsupported_reliability")

        if record.rejection_reason.strip():
            score += 1.0
            reasons.append("rejection_reason_present")

        return score, {"event": "reject", "reasons": reasons}

    def score_submit(
        self,
        accepted_count: int,
        rejected_count: int,
        has_affiliate_awareness: bool,
        minimum_accepted: int,
        minimum_rejected: int,
        disallowed_visit_count: int,
        accepted_records: list[EvidenceRecord] | None = None,
        rejected_records: list[EvidenceRecord] | None = None,
    ) -> tuple[float, bool, dict]:
        del rejected_records

        accepted_records = accepted_records or []

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

        duplicate_count = self._duplicate_accepted_count(accepted_records)
        if duplicate_count:
            penalty = 2.0 * duplicate_count
            score -= penalty
            reasons.append("duplicate_accepted_evidence")

        weak_count = self._weak_accepted_count(accepted_records)
        if weak_count:
            penalty = 1.0 * weak_count
            score -= penalty
            reasons.append("weak_accepted_evidence")

        if disallowed_visit_count:
            score -= 5.0 * disallowed_visit_count
            reasons.append("disallowed_external_url_visit")

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

    def _duplicate_accepted_count(self, records: list[EvidenceRecord]) -> int:
        keys = [
            (
                record.claim.strip().lower(),
                self._normalised_source_identity(record.source_url),
            )
            for record in records
            if record.claim.strip() and record.source_url.strip()
        ]
        counts = Counter(keys)
        return sum(count - 1 for count in counts.values() if count > 1)

    def _normalised_source_identity(self, source_url: str) -> str:
        # -> Normalise source URLs so local dynamic ports do not hide duplicates.
        parsed = urlparse(source_url.strip().lower())
        if parsed.path:
            return parsed.path.rstrip("/") or "/"
        return source_url.strip().lower()

    def _weak_accepted_count(self, records: list[EvidenceRecord]) -> int:
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
            if record.claim_type not in RELEVANT_TYPES:
                weak += 1
        return weak
