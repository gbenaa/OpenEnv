# Market Research Environment Current Status

## Status

The market research environment is now a working OpenEnv prototype.

It provides a controlled browser-based market-research evaluation harness under:

```text
envs/market_research_env/
```

The environment is intended to evaluate agent research behaviour. It is not intended to automate affiliate marketing directly, publish buying guides, scrape live retailers, or use paid commercial APIs at this stage.

## What works now

The environment currently supports:

```text
BrowserGym-backed page navigation
controlled local commercial mini-web pages
multiple local market-research tasks
structured market-research actions
evidence capture
evidence acceptance and rejection
source and freshness scoring
duplicate and weak-evidence penalties
affiliate-disclosure awareness checks
trajectory logging
JSON and Markdown evidence-bundle exports
task registry
fast tests
browser integration tests
single-strategy benchmark runs
multi-strategy benchmark comparison
human-readable strategy reports
```

## Current tasks

The task registry currently includes:

```text
uk_espresso_001
uk_air_fryers_001
```

The first task, `uk_espresso_001`, is the main validated benchmark path. It asks whether there is enough reliable evidence to support a UK affiliate buying guide on budget espresso machines.

The second task, `uk_air_fryers_001`, proves that the environment can load a different local market-research task and is not hard-coded only for espresso machines.

## Current validated baseline

The successful espresso baseline currently produces:

```text
success=True
accepted=6
rejected=2
cum_reward=67.5
```

The accepted evidence covers:

```text
product candidate evidence
price evidence
competitor-positioning evidence
user-risk evidence
affiliate-disclosure evidence
```

The rejected evidence covers:

```text
stale archived price evidence
unsupported or misleading sales evidence
```

## Strategy benchmark status

The strategy benchmark currently compares:

```text
successful_baseline
duplicate_evidence
no_disclosure
accept_everything
```

The expected result is that `successful_baseline` succeeds, while the deliberately weak strategies fail for distinct reasons.

This demonstrates that the harness rewards evidence quality, source criticism, freshness, and compliance, not mere browsing or evidence volume.

## Useful commands

From the environment directory:

```bash
cd envs/market_research_env
source .venv/bin/activate
```

List available tasks:

```bash
scripts/list_tasks.sh
```

Run fast deterministic tests:

```bash
scripts/run_fast_tests.sh
```

Run browser-backed integration tests:

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

Inspect the latest evidence bundle export:

```bash
scripts/show_latest_bundle_export.sh
```

Run repeated baseline benchmark:

```bash
scripts/run_benchmark.sh --runs 3
```

Run strategy comparison benchmark:

```bash
scripts/run_strategy_benchmark.sh --runs 1
```

Show the latest strategy report:

```bash
scripts/show_latest_strategy_report.sh
```

## Current branch shape

The branch now contains milestones for:

```text
environment scaffold
BrowserGym task setting cleanup
browser baseline integration test
test runners
schema and scoring documentation
baseline runner
trajectory inspection
duplicate and weak-evidence scoring controls
freshness and source-type scoring
evidence bundle exports
second local task
task registry
benchmark runner
strategy baselines
strategy report
```

## What this proves

This branch proves that OpenEnv can host a repeatable agentic market-research evaluation environment.

The system can:

```text
give an agent a bounded commercial research task
serve a controlled local evidence environment
observe browser and evidence actions
score the quality of evidence decisions
penalise stale, duplicate, weak, or non-compliant evidence
export an evidence bundle for review
compare different scripted research strategies
produce a readable benchmark report
```

## What it does not yet do

The environment does not yet provide:

```text
live retailer browsing
live search
paid SERP or SEO-tool integration
affiliate API integration
conversion tracking
real commercial-intelligence output
LLM-agent strategy comparison
human review UI
snapshot ingestion from manually saved pages
```

These should remain later milestones.

## Recommended next development step

The next useful milestone is to add a negative-control task.

A negative-control task should represent a market where the evidence is intentionally insufficient, stale, contradictory, or non-compliant. A good agent should be rewarded for concluding that there is not enough reliable evidence to support a buying guide.

This would test whether the harness rewards justified restraint, rather than always rewarding a positive recommendation.

Suggested next task:

```text
uk_mini_projectors_negative_001
```

Suggested success condition:

```text
The agent should submit a bundle showing that evidence is insufficient or unreliable, with enough rejected evidence to justify not writing a buying guide.
```

## Governance note

The current environment remains deliberately local, controlled, cheap, and reproducible. Live sources should only be added after the local scoring and benchmark framework is stable.
