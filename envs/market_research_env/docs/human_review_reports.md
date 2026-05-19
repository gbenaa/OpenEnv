# Human Review Reports

Human-review reports provide a reviewer-facing Markdown view over an exported evidence bundle.

They are intended for inspection and governance, not for automatic publication.

## Purpose

The report combines:

```text
episode score
success status
accepted evidence
rejected evidence
claim-type counts
score reasons
reviewer warnings
human checklist
```

This gives a human reviewer one file to inspect before any evidence bundle is used downstream.

## Command

Generate and print a report for the latest exported bundle:

```bash
cd envs/market_research_env
source .venv/bin/activate

scripts/run_baseline_episode.sh
scripts/show_latest_human_review_report.sh
```

By default, reports are written under:

```text
/tmp/market_research_env/bundles/human_reviews/
```

## What the report checks

The report warns if:

```text
no accepted evidence exists
no rejected evidence exists
affiliate-disclosure awareness is missing
pending evidence remains unresolved
the episode did not meet the current success condition
```

## Current limits

The report does not independently verify truth. It summarises what the controlled environment observed and how the episode was scored.

For real-world use, a human reviewer would still need to check live freshness, source suitability, and commercial compliance before publication.
