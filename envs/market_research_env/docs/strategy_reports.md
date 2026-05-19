# Strategy benchmark reports

The strategy benchmark runner compares the successful scripted baseline against deliberately weak strategies.

The report helper reads the latest strategy benchmark JSON and writes a clearer Markdown report with:

```text
strategy name
run count
success rate
mean reward
mean accepted evidence
mean rejected evidence
interpretation of likely failure mode
```

## Usage

Run a strategy benchmark:

```bash
scripts/run_strategy_benchmark.sh --runs 1
```

Then generate a readable report:

```bash
scripts/show_latest_strategy_report.sh
```

The report is written next to the benchmark JSON under:

```text
/tmp/market_research_env/benchmarks/
```

## Purpose

This report is intended to show that the environment rewards good evidence behaviour and penalises weak strategies such as:

```text
accepting everything
duplicating evidence
omitting affiliate-disclosure awareness
```

It is not a live commercial-intelligence report. It is a benchmark report for the controlled environment.
