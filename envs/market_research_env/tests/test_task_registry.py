from pathlib import Path
import json

import pytest

from market_research_env.server.task_registry import (
    build_task_index,
    list_tasks,
    load_task,
    write_task_index,
)


def test_task_registry_lists_packaged_tasks():
    tasks = list_tasks()
    task_ids = {task["task_id"] for task in tasks}

    assert "uk_espresso_001" in task_ids
    assert "uk_air_fryers_001" in task_ids


def test_task_registry_loads_packaged_task():
    task = load_task("uk_espresso_001")

    assert task["task_id"] == "uk_espresso_001"
    assert task["market"] == "UK"


def test_unknown_task_has_useful_error():
    with pytest.raises(FileNotFoundError) as exc_info:
        load_task("does_not_exist")

    assert "Unknown task_id" in str(exc_info.value)


def test_build_and_write_task_index(tmp_path: Path):
    task = {
        "task_id": "example_task",
        "market": "UK",
        "category": "example category",
        "objective": "Example objective.",
        "start_path": "/example/index.html",
        "max_steps": 7,
        "minimum_accepted_evidence": 2,
        "minimum_rejected_evidence": 1,
    }
    (tmp_path / "example_task.json").write_text(
        json.dumps(task),
        encoding="utf-8",
    )

    built = build_task_index(tmp_path)
    assert built[0]["task_id"] == "example_task"

    index_path = write_task_index(tmp_path)
    assert index_path.exists()

    listed = list_tasks(tmp_path)
    assert listed[0]["task_id"] == "example_task"
