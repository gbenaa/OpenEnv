# Market Research Environment Trajectory Logging

## Purpose

The environment writes JSONL trajectory logs so a browser episode can be inspected after it runs.

The log is intended to make the agent's behaviour auditable. It should show the reset event, each action, reward changes, errors, scoring details, and the final submitted bundle.

## Default location

By default, trajectory logs are written under:

```text
/tmp/market_research_env/trajectories/
```

Each completed episode writes one file:

```text
<episode_id>.jsonl
```

Each line is a JSON event.

## Event shape

A typical event has this shape:

```json
{
  "timestamp": "2026-05-19T19:07:28.000000Z",
  "event_type": "step",
  "payload": {
    "action": {
      "action_type": "capture_evidence"
    },
    "reward": 2.5,
    "done": false,
    "message": "Captured evidence ev_example.",
    "error": null,
    "score_details": {
      "event": "capture",
      "reasons": [
        "claim_present",
        "source_url_present",
        "relevant_claim_type",
        "rationale_present"
      ]
    }
  }
}
```

## Inspecting the latest trajectory

After running:

```bash
scripts/run_baseline_episode.sh
```

inspect the latest trajectory with:

```bash
scripts/show_latest_trajectory.sh
```

or:

```bash
python examples/show_latest_trajectory.py
```

## What to look for

A good baseline run should show:

```text
reset event
browser navigation actions
capture_evidence actions
accept_evidence actions
reject_evidence actions
submit_bundle action
positive final reward
success=True in final score details
```

## Why this matters

The trajectory log is the basis for later benchmarking. It allows the environment to compare agents not only by final score, but also by how they reached the result.

Future benchmark summaries can derive:

```text
total reward
success rate
accepted evidence count
rejected evidence count
duplicate evidence count
stale-evidence mistakes
unsupported-claim mistakes
disallowed URL visits
compliance failures
```

## Current limitation

The first logger is deliberately simple. It stores episode events as local JSONL files and does not yet provide:

```text
aggregate benchmark summaries
HTML reports
duplicate-evidence analysis
cross-run comparison
per-source statistics
```

Those belong to later milestones.
