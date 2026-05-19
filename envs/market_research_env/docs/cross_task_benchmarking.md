# Cross-Task Benchmarking

## Purpose

The cross-task benchmark checks that the environment can evaluate more than one kind of market-research outcome.

It currently runs:

```text
uk_espresso_001
uk_smart_rings_negative_001
```

The espresso task is a positive evidence-sufficiency case. The smart-rings task is a negative-control case where the intended conclusion is insufficient evidence.

## Command

From `envs/market_research_env`:

```bash
scripts/run_cross_task_benchmark.sh --runs 1
```

## Output

The script prints one line per task run, then a summary. It also writes JSON and Markdown outputs to:

```text
/tmp/market_research_env/cross_task_benchmarks/
```

## What this milestone proves

This benchmark shows that the harness is not limited to one scripted positive path. It can represent both:

```text
enough evidence to support a buying-guide decision
insufficient evidence, where weak sources should be rejected
```

This is an important guardrail for later LLM-agent evaluation, because the best agent should not always try to produce a recommendation.
