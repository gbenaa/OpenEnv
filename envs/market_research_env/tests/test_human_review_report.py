from pathlib import Path
import json

from market_research_env.server.human_review_report import (
    build_human_review_report,
    write_human_review_report,
)


def sample_payload():
    bundle = {
        "task_id": "uk_espresso_001",
        "accepted_evidence": [
            {
                "claim": "BrewStart Compact 15 Bar is listed at £149.",
                "claim_type": "price",
                "source_url": "http://127.0.0.1:1234/product_a.html",
                "freshness": "current",
                "reliability": "controlled_local_page",
                "rationale": "Current product price signal.",
                "compliance_notes": "",
                "extracted_text_excerpt": "Current listed price: £149",
            },
            {
                "claim": "Affiliate buying guides must disclose commission.",
                "claim_type": "affiliate",
                "source_url": "http://127.0.0.1:1234/affiliate_terms.html",
                "freshness": "current",
                "reliability": "controlled_local_page",
                "rationale": "Disclosure evidence.",
                "compliance_notes": "Affiliate disclosure awareness present.",
                "extracted_text_excerpt": "Qualifying purchases may generate commission.",
            },
        ],
        "rejected_evidence": [
            {
                "claim": "BrewStart Compact was £79 in a 2022 flash sale.",
                "claim_type": "price",
                "source_url": "http://127.0.0.1:1234/stale_price_page.html",
                "rejection_reason": "Stale archived price.",
                "rationale": "Archived claim.",
                "extracted_text_excerpt": "Archive date: 2022-11-04",
            }
        ],
        "pending_evidence": [],
        "cum_reward": 67.5,
        "submitted": True,
    }
    return {
        "episode_id": "episode_test",
        "task_id": "uk_espresso_001",
        "bundle": bundle,
        "cum_reward": 67.5,
        "score_details": {
            "success": True,
            "reasons": [
                "accepted_evidence_threshold_met",
                "rejected_evidence_threshold_met",
                "affiliate_disclosure_awareness_present",
            ],
        },
    }


def test_build_human_review_report_contains_core_sections():
    report = build_human_review_report(sample_payload())

    assert "# Human Review Report" in report
    assert "## Episode summary" in report
    assert "## Accepted evidence" in report
    assert "## Rejected evidence" in report
    assert "## Reviewer warnings" in report
    assert "No immediate reviewer warnings detected" in report


def test_write_human_review_report(tmp_path: Path):
    bundle_path = tmp_path / "episode_test.json"
    bundle_path.write_text(json.dumps(sample_payload()), encoding="utf-8")

    report_path = write_human_review_report(bundle_path)

    assert report_path.exists()
    text = report_path.read_text(encoding="utf-8")
    assert "BrewStart Compact 15 Bar" in text
    assert "Stale archived price" in text
