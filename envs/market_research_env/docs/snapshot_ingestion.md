# Manual Snapshot Ingestion

## Purpose

Manual snapshot ingestion is the next step between the fully controlled mini-web and live external web access.

It allows the environment to use saved HTML pages as repeatable evidence sources while avoiding live scraping, paid search APIs, or volatile retailer pages.

## Why this matters

The current local mini-web is deterministic and useful for testing the harness. Manual snapshots make the harness more realistic without losing repeatability.

A saved snapshot can preserve:

```text
original source URL
observation timestamp
source type
saved local path
task association
page title
```

This means an agent can later be evaluated on saved pages that were manually collected or legally exported, while the benchmark remains reproducible.

## Current implementation

The initial snapshot registry is stored at:

```text
data/snapshots/index.json
```

The first example snapshot set is:

```text
espresso_manual_snapshot_001
```

It is associated with:

```text
uk_espresso_001
```

The example pages are copied from the controlled local evidence pattern so the ingestion path can be tested without introducing live sources.

## Listing snapshots

From the environment directory:

```bash
scripts/list_snapshots.sh
```

Expected shape:

```text
espresso_manual_snapshot_001 | uk_espresso_001 | UK | budget espresso machines | pages=2
```

## What this does not yet do

This milestone does not yet make the browser automatically browse saved snapshots during an episode.

It adds the registry, metadata model, loader, CLI listing tool, documentation, and tests. The next implementation step would be to allow a task to choose between:

```text
controlled_local_web
manual_snapshot
```

## Future work

Likely next steps:

1. Add a snapshot-backed task mode.
2. Serve snapshot pages through the same local web server.
3. Preserve original source URL separately from local served URL.
4. Add scoring rules for manual snapshots.
5. Add snapshot freshness and provenance checks.
