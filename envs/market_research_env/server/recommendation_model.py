"""Recommendation-facing evidence model for market-research bundles."""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, Field


PRICE_RE = re.compile(r"£\s?\d+(?:\.\d{2})?")


class ProductRecommendationSignal(BaseModel):
    """Structured product signal derived from accepted market-research evidence."""

    product_name: str = Field(default="")
    price_observed: str = Field(default="")
    availability: str = Field(default="")
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    target_user: str = Field(default="")
    risk_notes: list[str] = Field(default_factory=list)
    source_urls: list[str] = Field(default_factory=list)
    source_confidence: str = Field(default="unknown")
    recommendation_relevance: str = Field(default="unknown")
    evidence_ids: list[str] = Field(default_factory=list)


class RecommendationEvidenceSummary(BaseModel):
    """Recommendation-facing summary derived from an evidence bundle."""

    task_id: str = Field(default="")
    product_signals: list[ProductRecommendationSignal] = Field(default_factory=list)
    risk_notes: list[str] = Field(default_factory=list)
    compliance_notes: list[str] = Field(default_factory=list)
    rejected_claims: list[str] = Field(default_factory=list)
    source_count: int = Field(default=0)


KNOWN_PRODUCTS = [
    "BrewStart Compact 15 Bar",
    "CremaGo Manual Espresso",
    "BaristaLite Mini",
]


def _normalise_bundle(payload: dict[str, Any]) -> dict[str, Any]:
    """Return the bundle whether payload is wrapped or already bundle-shaped."""
    if "bundle" in payload and isinstance(payload["bundle"], dict):
        return payload["bundle"]
    return payload


def _first_price(text: str) -> str:
    match = PRICE_RE.search(text or "")
    return match.group(0).replace(" ", "") if match else ""


def _infer_product_name(text: str) -> str:
    for product in KNOWN_PRODUCTS:
        if product.lower() in (text or "").lower():
            return product
    return ""


def _confidence_from_record(record: dict[str, Any]) -> str:
    if record.get("freshness") == "current" and record.get("reliability") == "controlled_local_page":
        return "high_controlled"
    if record.get("reliability") == "unsupported":
        return "low"
    return "unknown"


def build_recommendation_summary(payload: dict[str, Any]) -> RecommendationEvidenceSummary:
    """Build a recommendation-facing summary from an exported evidence bundle."""

    bundle = _normalise_bundle(payload)
    accepted = list(bundle.get("accepted_evidence", []))
    rejected = list(bundle.get("rejected_evidence", []))

    by_product: dict[str, ProductRecommendationSignal] = {}
    general_risks: list[str] = []
    compliance_notes: list[str] = []

    for record in accepted:
        claim = str(record.get("claim", ""))
        excerpt = str(record.get("extracted_text_excerpt", ""))
        combined = f"{claim} {excerpt}"
        claim_type = str(record.get("claim_type", "general"))
        product_name = _infer_product_name(combined)

        if claim_type in {"risk", "review"} and not product_name:
            if claim:
                general_risks.append(claim)
            continue

        if claim_type in {"affiliate", "compliance"}:
            note = record.get("compliance_notes") or claim
            if note:
                compliance_notes.append(str(note))
            continue

        if not product_name:
            continue

        signal = by_product.setdefault(
            product_name,
            ProductRecommendationSignal(
                product_name=product_name,
                source_confidence=_confidence_from_record(record),
                recommendation_relevance="candidate",
            ),
        )

        price = _first_price(combined)
        if price and not signal.price_observed:
            signal.price_observed = price

        if "in stock" in combined.lower():
            signal.availability = "in stock"
        elif "limited stock" in combined.lower():
            signal.availability = "limited stock"

        if claim and claim not in signal.pros:
            signal.pros.append(claim)

        if "risk" in combined.lower() or "weakness" in combined.lower() or "noisy" in combined.lower():
            if excerpt and excerpt not in signal.risk_notes:
                signal.risk_notes.append(excerpt)

        source_url = str(record.get("source_url", ""))
        if source_url and source_url not in signal.source_urls:
            signal.source_urls.append(source_url)

        evidence_id = str(record.get("evidence_id", ""))
        if evidence_id and evidence_id not in signal.evidence_ids:
            signal.evidence_ids.append(evidence_id)

    rejected_claims = [
        str(record.get("claim", ""))
        for record in rejected
        if record.get("claim")
    ]

    all_source_urls = {
        str(record.get("source_url", ""))
        for record in accepted + rejected
        if record.get("source_url")
    }

    return RecommendationEvidenceSummary(
        task_id=str(bundle.get("task_id", "")),
        product_signals=list(by_product.values()),
        risk_notes=general_risks,
        compliance_notes=compliance_notes,
        rejected_claims=rejected_claims,
        source_count=len(all_source_urls),
    )


def summary_to_markdown(summary: RecommendationEvidenceSummary) -> str:
    """Render a recommendation-facing summary as Markdown."""

    lines: list[str] = [
        "# Recommendation Evidence Summary",
        "",
        f"Task: `{summary.task_id}`",
        f"Source count: {summary.source_count}",
        "",
        "## Product signals",
        "",
    ]

    if not summary.product_signals:
        lines.append("No product signals found.")
    else:
        for signal in summary.product_signals:
            lines.extend(
                [
                    f"### {signal.product_name}",
                    "",
                    f"- Price observed: {signal.price_observed or 'unknown'}",
                    f"- Availability: {signal.availability or 'unknown'}",
                    f"- Source confidence: {signal.source_confidence}",
                    f"- Recommendation relevance: {signal.recommendation_relevance}",
                    "",
                ]
            )
            if signal.pros:
                lines.append("Pros or evidence claims:")
                for item in signal.pros:
                    lines.append(f"- {item}")
                lines.append("")
            if signal.risk_notes:
                lines.append("Risk notes:")
                for item in signal.risk_notes:
                    lines.append(f"- {item}")
                lines.append("")

    lines.extend(["## General risk notes", ""])
    if summary.risk_notes:
        for item in summary.risk_notes:
            lines.append(f"- {item}")
    else:
        lines.append("No general risk notes found.")

    lines.extend(["", "## Compliance notes", ""])
    if summary.compliance_notes:
        for item in summary.compliance_notes:
            lines.append(f"- {item}")
    else:
        lines.append("No compliance notes found.")

    lines.extend(["", "## Rejected claims", ""])
    if summary.rejected_claims:
        for item in summary.rejected_claims:
            lines.append(f"- {item}")
    else:
        lines.append("No rejected claims found.")

    return "\n".join(lines) + "\n"
