"""Human-review report generation for market-research evidence bundles."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any
import json


def load_bundle_json(path: str | Path) -> dict[str, Any]:
    """Load an exported bundle JSON file."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalise_export_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a consistent top-level bundle view.

    -> Export files intentionally preserve both a wrapped `bundle` object and
       top-level convenience fields. This helper keeps the report code tolerant
       of either shape.
    """
    bundle = dict(payload.get("bundle") or {})

    for key in [
        "task_id",
        "accepted_evidence",
        "rejected_evidence",
        "pending_evidence",
        "cum_reward",
        "submitted",
        "export_paths",
    ]:
        if key not in bundle and key in payload:
            bundle[key] = payload[key]

    if "score_details" not in bundle:
        bundle["score_details"] = payload.get("score_details", {})

    bundle.setdefault("accepted_evidence", [])
    bundle.setdefault("rejected_evidence", [])
    bundle.setdefault("pending_evidence", [])
    bundle.setdefault("cum_reward", 0.0)
    bundle.setdefault("submitted", False)
    bundle.setdefault("task_id", payload.get("task_id", ""))

    return bundle


def _claim_type_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(str(record.get("claim_type") or "unknown") for record in records)
    return dict(sorted(counts.items()))


def _has_affiliate_awareness(bundle: dict[str, Any]) -> bool:
    values: list[str] = []
    for record in bundle.get("accepted_evidence", []) + bundle.get("rejected_evidence", []):
        values.extend(
            [
                str(record.get("claim", "")),
                str(record.get("rationale", "")),
                str(record.get("compliance_notes", "")),
                str(record.get("extracted_text_excerpt", "")),
            ]
        )
    text = " ".join(values).lower()
    return any(marker in text for marker in ["affiliate", "commission", "disclosure", "prices and availability"])


def build_human_review_report(
    payload: dict[str, Any],
    source_path: str | Path | None = None,
) -> str:
    """Build a reviewer-facing Markdown report for an exported bundle."""
    bundle = normalise_export_payload(payload)
    score_details = payload.get("score_details") or bundle.get("score_details") or {}

    accepted = bundle.get("accepted_evidence", [])
    rejected = bundle.get("rejected_evidence", [])
    pending = bundle.get("pending_evidence", [])

    reasons = score_details.get("reasons", [])
    success = score_details.get("success", payload.get("success"))

    accepted_counts = _claim_type_counts(accepted)
    rejected_counts = _claim_type_counts(rejected)

    warnings: list[str] = []
    if not accepted:
        warnings.append("No accepted evidence was submitted.")
    if not rejected:
        warnings.append("No rejected evidence was submitted, so source criticism may be weak.")
    if not _has_affiliate_awareness(bundle):
        warnings.append("No affiliate-disclosure awareness was detected.")
    if pending:
        warnings.append(f"{len(pending)} pending evidence item(s) were not resolved.")
    if success is not True:
        warnings.append("The episode did not meet the current success condition.")

    lines: list[str] = []
    lines.append("# Human Review Report")
    lines.append("")
    if source_path:
        lines.append(f"Source bundle: `{source_path}`")
        lines.append("")

    lines.append("## Episode summary")
    lines.append("")
    lines.append(f"- Task: `{bundle.get('task_id', '')}`")
    lines.append(f"- Submitted: `{bundle.get('submitted')}`")
    lines.append(f"- Success: `{success}`")
    lines.append(f"- Cumulative reward: `{bundle.get('cum_reward')}`")
    lines.append(f"- Accepted evidence: `{len(accepted)}`")
    lines.append(f"- Rejected evidence: `{len(rejected)}`")
    lines.append(f"- Pending evidence: `{len(pending)}`")
    lines.append("")

    lines.append("## Score reasons")
    lines.append("")
    if reasons:
        for reason in reasons:
            lines.append(f"- {reason}")
    else:
        lines.append("- No score reasons recorded.")
    lines.append("")

    lines.append("## Evidence profile")
    lines.append("")
    lines.append("Accepted claim types:")
    if accepted_counts:
        for claim_type, count in accepted_counts.items():
            lines.append(f"- {claim_type}: {count}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("Rejected claim types:")
    if rejected_counts:
        for claim_type, count in rejected_counts.items():
            lines.append(f"- {claim_type}: {count}")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## Accepted evidence")
    lines.append("")
    if accepted:
        for index, record in enumerate(accepted, start=1):
            lines.append(f"### {index}. {record.get('claim', '')}")
            lines.append("")
            lines.append(f"- Type: `{record.get('claim_type', '')}`")
            lines.append(f"- Source: `{record.get('source_url', '')}`")
            lines.append(f"- Freshness: `{record.get('freshness', '')}`")
            lines.append(f"- Reliability: `{record.get('reliability', '')}`")
            rationale = record.get("rationale", "")
            if rationale:
                lines.append(f"- Rationale: {rationale}")
            compliance_notes = record.get("compliance_notes", "")
            if compliance_notes:
                lines.append(f"- Compliance notes: {compliance_notes}")
            excerpt = str(record.get("extracted_text_excerpt", "")).strip()
            if excerpt:
                excerpt = excerpt.replace("\n", " ")
                lines.append("")
                lines.append("> " + excerpt[:600])
            lines.append("")
    else:
        lines.append("No accepted evidence.")
        lines.append("")

    lines.append("## Rejected evidence")
    lines.append("")
    if rejected:
        for index, record in enumerate(rejected, start=1):
            lines.append(f"### {index}. {record.get('claim', '')}")
            lines.append("")
            lines.append(f"- Type: `{record.get('claim_type', '')}`")
            lines.append(f"- Source: `{record.get('source_url', '')}`")
            lines.append(f"- Reason: {record.get('rejection_reason', '')}")
            rationale = record.get("rationale", "")
            if rationale:
                lines.append(f"- Rationale: {rationale}")
            excerpt = str(record.get("extracted_text_excerpt", "")).strip()
            if excerpt:
                excerpt = excerpt.replace("\n", " ")
                lines.append("")
                lines.append("> " + excerpt[:600])
            lines.append("")
    else:
        lines.append("No rejected evidence.")
        lines.append("")

    lines.append("## Reviewer warnings")
    lines.append("")
    if warnings:
        for warning in warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- No immediate reviewer warnings detected.")
    lines.append("")

    lines.append("## Human review checklist")
    lines.append("")
    lines.append("- Confirm that accepted evidence supports the intended commercial conclusion.")
    lines.append("- Confirm that rejected evidence was correctly excluded.")
    lines.append("- Check that price and availability claims are not treated as permanent.")
    lines.append("- Check that affiliate-disclosure awareness is present before any user-facing output.")
    lines.append("- Check whether a human should verify source freshness before publication.")
    lines.append("")

    return "\n".join(lines)


def write_human_review_report(
    bundle_json_path: str | Path,
    output_dir: str | Path | None = None,
) -> Path:
    """Write a human-review Markdown report for an exported bundle."""
    source_path = Path(bundle_json_path)
    payload = load_bundle_json(source_path)
    report = build_human_review_report(payload, source_path=source_path)

    target_dir = Path(output_dir) if output_dir is not None else source_path.parent / "human_reviews"
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / f"{source_path.stem}_human_review.md"
    target_path.write_text(report, encoding="utf-8")
    return target_path


def find_latest_bundle_json(bundle_dir: str | Path = "/tmp/market_research_env/bundles") -> Path:
    """Return the newest exported bundle JSON file."""
    directory = Path(bundle_dir)
    candidates = sorted(directory.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not candidates:
        raise FileNotFoundError(f"No bundle JSON files found in {directory}")
    return candidates[0]
