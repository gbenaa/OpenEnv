# Market Research Benchmarking

## Purpose

The benchmark runner repeats the known-good espresso baseline and writes a compact summary.

This is the first step towards comparing agents, prompts, and strategies on the same bounded market-research task.

## Command

From the environment directory:

```bash
scripts/run_benchmark.sh --runs 3
```

## Output

Benchmark summaries are written to:

```text
/tmp/market_research_env/benchmarks/
```

Each run produces:

```text
JSON summary
Markdown summary
```

The summary includes:

```text
run count
success count
success rate
mean reward
minimum reward
maximum reward
per-run episode IDs
per-run accepted and rejected evidence counts
```

## Current scope

The first benchmark runner repeats the scripted espresso baseline only.

It does not yet compare multiple agents. It gives a stable benchmark output format that later agent strategies can reuse.

## Next benchmark extensions

Likely next steps:

1. Add a naive capture-everything baseline.
2. Add an accept-everything baseline.
3. Add a cautious evidence baseline.
4. Compare strategies on reward, success, duplicate evidence, rejected evidence, and compliance.
