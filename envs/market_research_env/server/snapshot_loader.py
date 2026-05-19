"""Manual snapshot loader for the market research environment."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SnapshotPage:
    """Metadata for a saved HTML snapshot page."""

    snapshot_id: str
    task_id: str
    snapshot_path: str
    source_url: str
    source_type: str
    observed_at: str
    title: str
    absolute_path: Path


@dataclass(frozen=True)
class SnapshotSet:
    """A group of saved pages associated with one task."""

    snapshot_id: str
    task_id: str
    market: str
    category: str
    source_mode: str
    created_at: str
    description: str
    pages: list[SnapshotPage]


class SnapshotRegistry:
    """Load and inspect saved snapshot metadata."""

    def __init__(self, root_dir: Path | None = None) -> None:
        package_root = Path(__file__).resolve().parents[1]
        self.root_dir = Path(root_dir) if root_dir else package_root / "data" / "snapshots"
        self.index_path = self.root_dir / "index.json"

    def load_index(self) -> dict[str, Any]:
        if not self.index_path.exists():
            return {"snapshots": []}
        return json.loads(self.index_path.read_text(encoding="utf-8"))

    def list_snapshots(self) -> list[SnapshotSet]:
        index = self.load_index()
        sets: list[SnapshotSet] = []

        for item in index.get("snapshots", []):
            snapshot_id = item["snapshot_id"]
            task_id = item["task_id"]
            pages = [
                SnapshotPage(
                    snapshot_id=snapshot_id,
                    task_id=task_id,
                    snapshot_path=page["snapshot_path"],
                    source_url=page["source_url"],
                    source_type=page.get("source_type", "manual_snapshot"),
                    observed_at=page.get("observed_at", ""),
                    title=page.get("title", ""),
                    absolute_path=self.root_dir / page["snapshot_path"],
                )
                for page in item.get("pages", [])
            ]
            sets.append(
                SnapshotSet(
                    snapshot_id=snapshot_id,
                    task_id=task_id,
                    market=item.get("market", ""),
                    category=item.get("category", ""),
                    source_mode=item.get("source_mode", "manual_snapshot"),
                    created_at=item.get("created_at", ""),
                    description=item.get("description", ""),
                    pages=pages,
                )
            )

        return sets

    def get_snapshot(self, snapshot_id: str) -> SnapshotSet:
        for snapshot in self.list_snapshots():
            if snapshot.snapshot_id == snapshot_id:
                return snapshot
        raise KeyError(f"Unknown snapshot_id: {snapshot_id}")

    def get_snapshots_for_task(self, task_id: str) -> list[SnapshotSet]:
        return [snapshot for snapshot in self.list_snapshots() if snapshot.task_id == task_id]

    def read_page_text(self, page: SnapshotPage) -> str:
        if not page.absolute_path.exists():
            raise FileNotFoundError(page.absolute_path)
        return page.absolute_path.read_text(encoding="utf-8")


def summarise_snapshots(registry: SnapshotRegistry | None = None) -> list[dict[str, Any]]:
    """Return compact snapshot metadata for CLI scripts and tests."""
    registry = registry or SnapshotRegistry()
    summaries: list[dict[str, Any]] = []

    for snapshot in registry.list_snapshots():
        summaries.append(
            {
                "snapshot_id": snapshot.snapshot_id,
                "task_id": snapshot.task_id,
                "market": snapshot.market,
                "category": snapshot.category,
                "source_mode": snapshot.source_mode,
                "created_at": snapshot.created_at,
                "page_count": len(snapshot.pages),
            }
        )

    return summaries
