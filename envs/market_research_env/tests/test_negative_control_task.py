import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_negative_control_task_file_exists_and_is_marked_negative():
    task_path = ROOT / "data" / "tasks" / "uk_smart_rings_negative_001.json"
    task = json.loads(task_path.read_text(encoding="utf-8"))

    assert task["task_id"] == "uk_smart_rings_negative_001"
    assert task["negative_control"] is True
    assert task["expected_conclusion"] == "insufficient_evidence"
    assert task["minimum_accepted_evidence"] == 1
    assert task["minimum_rejected_evidence"] == 3


def test_negative_control_local_pages_exist():
    page_dir = ROOT / "local_web" / "smart_rings_negative"

    for name in [
        "index.html",
        "product_claim.html",
        "forum_warning.html",
        "stale_review.html",
        "unsupported_claim.html",
        "affiliate_terms.html",
    ]:
        assert (page_dir / name).exists()


def test_negative_control_task_is_in_registry():
    index_path = ROOT / "data" / "tasks" / "index.json"
    registry = json.loads(index_path.read_text(encoding="utf-8"))
    task_ids = {item["task_id"] for item in registry["tasks"]}

    assert "uk_smart_rings_negative_001" in task_ids
