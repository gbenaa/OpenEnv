# Market Research Environment Branch Handover

## Purpose

This document summarises the current state of `envs/market_research_env/` on the `market-research-browser-env` branch.

The environment is a browser-based OpenEnv evaluation harness for controlled market-research tasks. It is not a live commercial-intelligence tool and it is not an affiliate-marketing automation system. It provides a repeatable way to test whether agents can browse authorised sources, capture evidence, reject weak evidence, submit bundles, and receive scores based on evidence quality.

## Current working state

The environment now supports:

```text
controlled local commercial mini-webs
BrowserGym-backed navigation
structured market-research actions
evidence capture
evidence acceptance and rejection
freshness and source-type scoring
duplicate and weak-evidence controls
affiliate-disclosure awareness checks
trajectory logging
JSON and Markdown evidence bundle exports
task registry
positive task
negative-control task
single-task benchmark
strategy benchmark
cross-task benchmark
```

## Main task coverage

The current task set includes:

```text
uk_espresso_001
uk_air_fryers_001
uk_smart_rings_negative_001
```

`uk_espresso_001` is the primary positive baseline task. It asks whether there is enough evidence to support a UK affiliate buying guide on budget espresso machines.

`uk_air_fryers_001` is a second local task proving that the environment is not hard-coded only for espresso machines.

`uk_smart_rings_negative_001` is a negative-control task. Its expected conclusion is that the evidence is insufficient.

## Core action model

The environment supports these action types:

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

The important distinction is that evidence actions are first-class actions. The environment evaluates not just navigation, but also evidence quality and source criticism.

## Evidence model

Captured evidence records preserve:

```text
evidence_id
claim
claim_type
source_url
observed_at
source_type
rationale
status
rejection_reason
reliability
freshness
commercial_usefulness
user_usefulness
compliance_notes
extracted_text_excerpt
metadata
```

## Current benchmark results

The positive espresso baseline currently succeeds with:

```text
task=uk_espresso_001
success=True
accepted=6
rejected=2
cum_reward=67.5
conclusion=sufficient_evidence
```

The negative-control smart-rings task currently succeeds as an insufficient-evidence case with:

```text
task=uk_smart_rings_negative_001
success=True
accepted=1
rejected=4
reward=36.25
conclusion=insufficient_evidence
```

The strategy benchmark distinguishes a successful baseline from deliberately bad strategies:

```text
successful_baseline -> success_rate=1.00
duplicate_evidence -> success_rate=0.00
no_disclosure -> success_rate=0.00
accept_everything -> success_rate=0.00
```

This shows that the harness rewards distinct, relevant evidence, source criticism, freshness, provenance, and affiliate-disclosure awareness rather than mere activity volume.

## How to run the environment

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

Inspect the latest trajectory:

```bash
scripts/show_latest_trajectory.sh
```

Inspect the latest exported evidence bundle:

```bash
scripts/show_latest_bundle_export.sh
```

List registered tasks:

```bash
scripts/list_tasks.sh
```

Run repeated baseline benchmark:

```bash
scripts/run_benchmark.sh --runs 3
```

Run strategy benchmark:

```bash
scripts/run_strategy_benchmark.sh --runs 1
scripts/show_latest_strategy_report.sh
```

Run cross-task benchmark:

```bash
scripts/run_cross_task_benchmark.sh --runs 1
```

## Output locations

Runtime outputs are written under:

```text
/tmp/market_research_env/
```

Important output directories include:

```text
/tmp/market_research_env/trajectories/
/tmp/market_research_env/bundles/
/tmp/market_research_env/benchmarks/
/tmp/market_research_env/cross_task_benchmarks/
```

These outputs are not committed to the repository. They are runtime artefacts for local inspection.

## What this branch proves

This branch proves that OpenEnv can provide the infrastructure for repeatable agentic market-research workflows.

It demonstrates:

```text
bounded task setup
browser-based interaction with controlled pages
commercial evidence capture
source and freshness evaluation
accept/reject evidence decisions
rewarding good evidence behaviour
penalising stale, weak, duplicated, or non-compliant evidence
trajectory logging
bundle export
strategy comparison
cross-task evaluation
```

It does not claim to produce live commercial truth. It is an evaluation harness for market-research behaviour.

## What is not yet implemented

The environment does not yet include:

```text
live retailer browsing
live search
paid SERP APIs
affiliate API integration
real price monitoring
conversion tracking
automated publishing
LLM-controlled autonomous agents
manual snapshot ingestion
human review UI
```

These should remain later-stage additions.

## Recommended next milestones

The next development steps should be:

1. Add manual snapshot ingestion so saved authorised pages can be used as repeatable task sources.
2. Add richer product-recommendation evidence fields such as product name, observed price, pros, cons, target user, risk notes, and recommendation relevance.
3. Add a human-review Markdown report for accepted and rejected evidence.
4. Add more negative-control tasks.
5. Add optional live-search integration only after snapshot-based workflows are stable.
6. Add LLM agent wrappers and compare them against scripted baselines.

## Suggested next thread prompt

```text
We are continuing work on gbenaa/OpenEnv branch market-research-browser-env.

Please inspect envs/market_research_env/, especially docs/current_status.md, docs/branch_handover.md, docs/schema_and_scoring.md, docs/benchmarking.md, docs/strategy_reports.md, and docs/cross_task_benchmarking.md.

The environment already has controlled local mini-web tasks, BrowserGym-backed navigation, evidence capture, accept/reject scoring, freshness/source scoring, duplicate/weak-evidence controls, trajectory logging, evidence bundle exports, task registry, strategy benchmark, and cross-task benchmark.

The next goal is to add manual snapshot ingestion for repeatable market-research tasks based on saved authorised pages. Do not start with live scraping or paid APIs. Preserve the current tests and benchmarks.
```

## Handover conclusion

The branch has reached a meaningful first working state. It now supports both positive and negative market-research evaluation cases, and it can compare good and bad strategies. The next useful step is to make the evidence sources more realistic while preserving repeatability.
