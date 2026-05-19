"""Task registry helpers for the market research environment."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def default_tasks_dir() -> Path:
    """Return the package task directory."""
    return Path(__file__).resolve().parents[1] / "data" / "tasks"


def load_task(task_id: str, tasks_dir: Path | None = None) -> dict[str, Any]:
    """Load a single task by task_id."""
    root = Path(tasks_dir) if tasks_dir is not None else default_tasks_dir()
    task_path = root / f"{task_id}.json"

    if not task_path.exists():
        available = ", ".join(task["task_id"] for task in list_tasks(root))
        raise FileNotFoundError(f"Unknown task_id {task_id!r}. Available tasks: {available}")

    return json.loads(task_path.read_text(encoding="utf-8"))


def build_task_index(tasks_dir: Path | None = None) -> list[dict[str, Any]]:
    """Build a task index from task JSON files.

    This ignores index.json itself, so the index can be regenerated deterministically.
    """
    root = Path(tasks_dir) if tasks_dir is not None else default_tasks_dir()
    tasks: list[dict[str, Any]] = []

    for task_path in sorted(root.glob("*.json")):
        if task_path.name == "index.json":
            continue

        task = json.loads(task_path.read_text(encoding="utf-8"))
        tasks.append(
            {
                "task_id": task.get("task_id", task_path.stem),
                "market": task.get("market", ""),
                "category": task.get("category", ""),
                "objective": task.get("objective", ""),
                "start_path": task.get("start_path", ""),
                "max_steps": task.get("max_steps", None),
                "minimum_accepted_evidence": task.get("minimum_accepted_evidence", None),
                "minimum_rejected_evidence": task.get("minimum_rejected_evidence", None),
            }
        )

    return tasks


def list_tasks(tasks_dir: Path | None = None) -> list[dict[str, Any]]:
    """Return the available task metadata.

    If index.json exists, use it. Otherwise build the index from task JSON files.
    """
    root = Path(tasks_dir) if tasks_dir is not None else default_tasks_dir()
    index_path = root / "index.json"

    if index_path.exists():
        payload = json.loads(index_path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            tasks = payload.get("tasks", [])
        else:
            tasks = payload
        return sorted(tasks, key=lambda item: item.get("task_id", ""))

    return build_task_index(root)


def write_task_index(tasks_dir: Path | None = None) -> Path:
    """Write index.json from the current task files."""
    root = Path(tasks_dir) if tasks_dir is not None else default_tasks_dir()
    index_path = root / "index.json"

    payload = {
        "tasks": build_task_index(root),
    }
    index_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return index_path
