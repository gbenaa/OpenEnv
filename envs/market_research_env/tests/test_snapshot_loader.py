from market_research_env.server.snapshot_loader import SnapshotRegistry, summarise_snapshots


def test_snapshot_registry_lists_example_snapshot():
    registry = SnapshotRegistry()
    snapshots = registry.list_snapshots()

    assert any(snapshot.snapshot_id == "espresso_manual_snapshot_001" for snapshot in snapshots)


def test_snapshot_registry_filters_by_task():
    registry = SnapshotRegistry()
    snapshots = registry.get_snapshots_for_task("uk_espresso_001")

    assert snapshots
    assert snapshots[0].task_id == "uk_espresso_001"


def test_snapshot_registry_page_paths_exist():
    registry = SnapshotRegistry()
    snapshot = registry.get_snapshot("espresso_manual_snapshot_001")

    assert snapshot.pages
    for page in snapshot.pages:
        assert page.absolute_path.exists()


def test_snapshot_registry_reads_page_text():
    registry = SnapshotRegistry()
    snapshot = registry.get_snapshot("espresso_manual_snapshot_001")
    text = registry.read_page_text(snapshot.pages[0])

    assert "BrewStart Compact" in text


def test_summarise_snapshots():
    summaries = summarise_snapshots()

    assert summaries
    assert summaries[0]["page_count"] >= 1
