"""Evidence store for market-research episodes."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from market_research_env.models import EvidenceRecord


def utc_now_iso() -> str:
    """Return a UTC timestamp suitable for evidence provenance."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class EvidenceStore:
    """In-memory evidence store for one episode."""

    def __init__(self) -> None:
        self._records: dict[str, EvidenceRecord] = {}

    def clear(self) -> None:
        self._records.clear()

    def capture(
        self,
        claim: str,
        claim_type: str,
        source_url: str,
        rationale: str = "",
        source_type: str = "controlled_local_page",
        reliability: str = "unknown",
        freshness: str = "unknown",
        commercial_usefulness: str = "unknown",
        user_usefulness: str = "unknown",
        compliance_notes: str = "",
        extracted_text_excerpt: str = "",
        metadata: dict | None = None,
    ) -> EvidenceRecord:
        evidence_id = f"ev_{uuid4().hex[:10]}"
        record = EvidenceRecord(
            evidence_id=evidence_id,
            claim=claim,
            claim_type=claim_type or "general",
            source_url=source_url,
            observed_at=utc_now_iso(),
            source_type=source_type,
            rationale=rationale,
            reliability=reliability,
            freshness=freshness,
            commercial_usefulness=commercial_usefulness,
            user_usefulness=user_usefulness,
            compliance_notes=compliance_notes,
            extracted_text_excerpt=extracted_text_excerpt[:800],
            metadata=metadata or {},
        )
        self._records[evidence_id] = record
        return record

    def get(self, evidence_id: str) -> EvidenceRecord:
        try:
            return self._records[evidence_id]
        except KeyError as exc:
            raise KeyError(f"Unknown evidence_id: {evidence_id}") from exc

    def accept(self, evidence_id: str) -> EvidenceRecord:
        record = self.get(evidence_id)
        record.status = "accepted"
        record.rejection_reason = ""
        return record

    def reject(self, evidence_id: str, reason: str) -> EvidenceRecord:
        record = self.get(evidence_id)
        record.status = "rejected"
        record.rejection_reason = reason
        return record

    def all(self) -> list[EvidenceRecord]:
        return list(self._records.values())

    def pending(self) -> list[EvidenceRecord]:
        return [record for record in self._records.values() if record.status == "pending"]

    def accepted(self) -> list[EvidenceRecord]:
        return [record for record in self._records.values() if record.status == "accepted"]

    def rejected(self) -> list[EvidenceRecord]:
        return [record for record in self._records.values() if record.status == "rejected"]
