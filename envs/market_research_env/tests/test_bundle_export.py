from pathlib import Path
import json

from market_research_env.server.exporters import write_evidence_bundle_exports


def test_write_evidence_bundle_exports(tmp_path: Path):
    bundle = {
        "task_id": "uk_espresso_001",
        "accepted_evidence": [
            {
                "claim": "Product A is listed at £149.",
                "claim_type": "price",
                "source_url": "http://127.0.0.1:1234/product_a.html",
                "observed_at": "2026-05-19T14:00:00Z",
                "source_type": "controlled_local_page",
                "freshness": "current",
                "reliability": "controlled_local_page",
                "rationale": "Current product price signal.",
                "status": "accepted",
                "extracted_text_excerpt": "Current listed price: £149",
            }
        ],
        "rejected_evidence": [],
        "pending_evidence": [],
        "cum_reward": 67.5,
        "submitted": True,
    }
    score_details = {
        "success": True,
        "reasons": ["accepted_evidence_threshold_met"],
    }

    paths = write_evidence_bundle_exports(
        output_dir=tmp_path,
        episode_id="episode_test",
        bundle=bundle,
        score_details=score_details,
    )

    json_path = Path(paths["json"])
    markdown_path = Path(paths["markdown"])

    assert json_path.exists()
    assert markdown_path.exists()

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["episode_id"] == "episode_test"
    assert payload["bundle"]["task_id"] == "uk_espresso_001"

    markdown = markdown_path.read_text(encoding="utf-8")
    assert "Market Research Evidence Bundle" in markdown
    assert "Product A is listed at £149." in markdown
