# Market Research Environment PR Summary

## Overview

This branch adds a new OpenEnv environment:

```text
envs/market_research_env/
```

The environment is a controlled browser-based market-research evaluation harness. It is designed to test whether agents can gather, criticise, accept, reject, score, export, and review commercial evidence under repeatable conditions.

It is not a live affiliate-marketing system, a scraper, a product-ranking engine, or an automated publishing workflow.

## What this branch adds

The branch adds:

```text
controlled local commercial mini-webs
BrowserGym-backed browsing
structured market-research actions
evidence capture
accept and reject evidence decisions
scoring based on evidence quality
duplicate and weak-evidence controls
freshness and source-type scoring
evidence bundle exports
recommendation evidence summaries
human review reports
task registry
manual snapshot ingestion support
positive and negative-control tasks
repeated-run benchmark tooling
strategy comparison reports
cross-task benchmark reports
documentation and test runners
```

## Main environment path

```text
envs/market_research_env/
```

## Current tasks

The environment currently includes:

```text
uk_espresso_001
uk_air_fryers_001
uk_smart_rings_negative_001
```

The espresso task is a positive task where the scripted baseline can gather enough evidence to support a buying-guide decision.

The smart-rings negative-control task is intended to represent an insufficient-evidence case, where a good agent should avoid overconfident commercial conclusions.

## Core action model

Supported action types include:

```text
goto
click
fill
scroll
extract_page_text
extract_links
capture_evidence
accept_evidence
reject_evidence
submit_bundle
noop
```

The important design point is that evidence handling is first-class. The harness is not merely measuring browser navigation. It evaluates which claims are captured, which are accepted, which are rejected, and why.

## What the benchmark proves

The current benchmark demonstrates that the harness can distinguish successful and weak strategies.

A successful strategy:

```text
captures distinct relevant evidence
preserves provenance
rejects stale or unsupported evidence
includes affiliate-disclosure awareness
submits a valid evidence bundle
```

Weak strategies fail for distinct reasons:

```text
accept_everything accepts stale or unsupported evidence
duplicate_evidence repeats the same evidence pattern
no_disclosure submits without sufficient affiliate-disclosure awareness
```

The cross-task benchmark also demonstrates that the environment can score both:

```text
sufficient_evidence
insufficient_evidence
```

This matters because a market-research harness should not always reward positive commercial conclusions. Sometimes the correct conclusion is that evidence is inadequate.

## How to run

From the environment directory:

```bash
cd envs/market_research_env
source .venv/bin/activate
```

Run fast tests:

```bash
scripts/run_fast_tests.sh
```

Run browser integration tests:

```bash
scripts/run_integration_tests.sh
```

Run all tests:

```bash
scripts/run_all_tests.sh
```

Run the successful baseline:

```bash
scripts/run_baseline_episode.sh
```

Inspect the latest exported bundle:

```bash
scripts/show_latest_bundle_export.sh
```

Inspect the latest trajectory:

```bash
scripts/show_latest_trajectory.sh
```

Inspect the latest recommendation summary:

```bash
scripts/show_latest_recommendation_summary.sh
```

Inspect the latest human review report:

```bash
scripts/show_latest_human_review_report.sh
```

Run repeated-run benchmark:

```bash
scripts/run_benchmark.sh --runs 3
```

Run strategy comparison benchmark:

```bash
scripts/run_strategy_benchmark.sh --runs 1
scripts/show_latest_strategy_report.sh
```

Run cross-task benchmark:

```bash
scripts/run_cross_task_benchmark.sh --runs 1
```

List available tasks:

```bash
scripts/list_tasks.sh
```

List available snapshots:

```bash
scripts/list_snapshots.sh
```

## Expected outputs

Evidence bundles are written under:

```text
/tmp/market_research_env/bundles/
```

Trajectory logs are written under:

```text
/tmp/market_research_env/trajectories/
```

Benchmark outputs are written under:

```text
/tmp/market_research_env/benchmarks/
```

Cross-task benchmark outputs are written under:

```text
/tmp/market_research_env/cross_task_benchmarks/
```

## Review checklist

A reviewer should check that:

```text
the new environment is isolated under envs/market_research_env/
OpenEnv core is not modified unnecessarily
the BrowserGym-backed baseline runs
fast and integration tests pass
bundle exports contain accepted and rejected evidence
human review reports are readable
strategy benchmarks distinguish good and bad strategies
negative-control tasks reward insufficient-evidence conclusions
documentation explains current scope and limitations
```

## Out of scope

This branch deliberately does not add:

```text
live retailer scraping
live Google search
paid SERP APIs
affiliate API integration
conversion tracking
automated publishing
production recommendation ranking
real commercial claims
```

The current purpose is to create a repeatable evaluation harness, not to generate live commercial intelligence.

## Known limitations

The current agent strategies are scripted.

The local pages are synthetic.

The reward model is still simple and should be treated as a first benchmark design, not a final commercial-quality scoring system.

The recommendation evidence model is a structured summary layer over controlled evidence, not a full product recommendation engine.

## Suggested next development step

The next useful development step is to add optional cached SERP-style pages or richer manual snapshot workflows. This would increase source realism without introducing live scraping or paid APIs.

A later step could introduce live authorised search only behind explicit configuration and separate non-deterministic tests.
