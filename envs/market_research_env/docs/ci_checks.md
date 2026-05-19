# GitHub Actions checks

This environment includes a lightweight GitHub Actions workflow:

```text
.github/workflows/market-research-env-fast-tests.yml
```

The workflow runs the market-research environment fast tests on pull requests and pushes that touch:

```text
envs/market_research_env/**
.github/workflows/market-research-env-fast-tests.yml
```

## Why only fast tests in CI

The fast tests cover deterministic behaviour:

```text
task registry
snapshot loading
evidence storage
scoring
freshness and source controls
duplicate and weak-evidence controls
bundle export helpers
recommendation summaries
human-review report helpers
benchmark summaries
cross-task summary logic
```

Browser-backed integration tests remain local for now because they require BrowserGym and Playwright browser runtime setup. Those tests should still be run locally before substantial changes:

```bash
cd envs/market_research_env
source .venv/bin/activate

scripts/run_integration_tests.sh
scripts/run_baseline_episode.sh
scripts/run_cross_task_benchmark.sh --runs 1
```

## Intended role

The CI workflow is a first review gate. It is not a complete validation suite.

It is intended to catch deterministic regressions quickly without introducing live web dependencies, paid APIs, or non-deterministic browser setup into CI.
