"""List manual snapshot sets for the market research environment."""

from __future__ import annotations

from market_research_env.server.snapshot_loader import SnapshotRegistry


def main() -> None:
    registry = SnapshotRegistry()
    snapshots = registry.list_snapshots()

    if not snapshots:
        print("No snapshots found.")
        return

    for snapshot in snapshots:
        print(
            f"{snapshot.snapshot_id} | {snapshot.task_id} | "
            f"{snapshot.market} | {snapshot.category} | pages={len(snapshot.pages)}"
        )
        for page in snapshot.pages:
            print(f"  - {page.title} -> {page.snapshot_path}")


if __name__ == "__main__":
    main()
