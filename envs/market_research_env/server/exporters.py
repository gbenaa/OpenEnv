"""Evidence bundle export helpers for the market research environment."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


def _utc_now_iso() -> str:
    """Return a UTC timestamp for export metadata."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _records(bundle: dict[str, Any], key: str) -> list[dict[str, Any]]:
    """Return a normalised list of evidence records from a bundle."""
    value = bundle.get(key, [])
    if isinstance(value, list):
        return value
    return []


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    """Write a human-readable Markdown export."""
    bundle = payload["bundle"]
    score_details = payload.get("score_details", {})

    lines: list[str] = []
    lines.append("# Market Research Evidence Bundle")
    lines.append("")
    lines.append(f"Episode ID: `{payload.get('episode_id', '')}`")
    lines.append(f"Task ID: `{bundle.get('task_id', '')}`")
    lines.append(f"Submitted: `{bundle.get('submitted', False)}`")
    lines.append(f"Success: `{score_details.get('success', False)}`")
    lines.append(f"Cumulative reward: `{bundle.get('cum_reward', 0.0)}`")
    lines.append("")

    reasons = score_details.get("reasons", [])
    if reasons:
        lines.append("## Score reasons")
        lines.append("")
        for reason in reasons:
            lines.append(f"- {reason}")
        lines.append("")

    sections = [
        ("Accepted evidence", "accepted_evidence"),
        ("Rejected evidence", "rejected_evidence"),
        ("Pending evidence", "pending_evidence"),
    ]

    for title, key in sections:
        records = _records(bundle, key)
        lines.append(f"## {title}")
        lines.append("")
        if not records:
            lines.append("_None._")
            lines.append("")
            continue

        for index, record in enumerate(records, start=1):
            claim = record.get("claim", "")
            lines.append(f"### {index}. {claim}")
            lines.append("")
            lines.append(f"- Evidence ID: `{record.get('evidence_id', '')}`")
            lines.append(f"- Claim type: `{record.get('claim_type', '')}`")
            lines.append(f"- Status: `{record.get('status', '')}`")
            lines.append(f"- Source URL: {record.get('source_url', '')}")
            lines.append(f"- Source type: `{record.get('source_type', '')}`")
            lines.append(f"- Freshness: `{record.get('freshness', '')}`")
            lines.append(f"- Reliability: `{record.get('reliability', '')}`")
            lines.append(f"- Rationale: {record.get('rationale', '')}")

            rejection_reason = record.get("rejection_reason", "")
            if rejection_reason:
                lines.append(f"- Rejection reason: {rejection_reason}")

            compliance_notes = record.get("compliance_notes", "")
            if compliance_notes:
                lines.append(f"- Compliance notes: {compliance_notes}")

            excerpt = record.get("extracted_text_excerpt", "")
            if excerpt:
                quoted_excerpt = str(excerpt).replace("\n", " ")
                lines.append("")
                lines.append("> " + quoted_excerpt)

            lines.append("")

    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_evidence_bundle_exports(
    output_dir: str | Path,
    episode_id: str,
    bundle: dict[str, Any],
    score_details: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Write JSON and Markdown exports for an evidence bundle.

    The JSON intentionally supports two access patterns:
    -> Top-level bundle fields such as `cum_reward`, for simple integration checks.
    -> A nested `bundle` object, for consumers that expect a wrapper format.
    """

    score_details = score_details or {}
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    json_path = output_path / f"{episode_id}.json"
    markdown_path = output_path / f"{episode_id}.md"

    export_paths = {
        "json": str(json_path),
        "markdown": str(markdown_path),
    }

    bundle_copy = deepcopy(bundle)
    bundle_copy["export_paths"] = export_paths

    payload: dict[str, Any] = {
        "episode_id": episode_id,
        "exported_at": _utc_now_iso(),
        "score_details": score_details,
        "bundle": bundle_copy,
    }

    # -> Mirror the bundle fields at top level for lightweight consumers.
    payload.update(bundle_copy)

    # -> Convenience aliases for summary tools.
    payload["success"] = bool(score_details.get("success", False))
    payload["reasons"] = list(score_details.get("reasons", []))

    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    _write_markdown(markdown_path, payload)

    return export_paths
