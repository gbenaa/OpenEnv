# Strategy baselines

The strategy benchmark adds deliberately poor baselines so the environment can
show that its scoring model distinguishes useful market-research behaviour from
weak or non-compliant behaviour.

## Strategies

```text
successful_baseline
accept_everything
duplicate_evidence
no_disclosure
```

## Expected interpretation

`successful_baseline` should succeed because it accepts current, relevant
evidence, rejects stale or unsupported claims, and includes affiliate-disclosure
awareness.

`accept_everything` should score worse because it accepts stale and unsupported
claims, and it does not satisfy the rejected-evidence threshold.

`duplicate_evidence` should score worse or fail because it repeats the same
accepted claim and source path to game the evidence threshold.

`no_disclosure` should fail because it omits affiliate-disclosure awareness.

## Run

```bash
cd envs/market_research_env
source .venv/bin/activate

scripts/run_strategy_benchmark.sh --runs 1
```

The script writes JSON and Markdown summaries to:

```text
/tmp/market_research_env/benchmarks/
```
