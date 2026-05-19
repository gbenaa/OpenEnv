# Evidence Bundle Exports

The market research environment writes a final evidence bundle when an episode submits.

Exports are written under:

```text
/tmp/market_research_env/bundles/
```

or under the directory set by:

```bash
MARKET_RESEARCH_OUTPUT_DIR=/path/to/output
```

## Export formats

Each submitted episode writes:

```text
<episode_id>.json
<episode_id>.md
```

The JSON export is intended for downstream processing.

The Markdown export is intended for human review.

## JSON shape

The JSON export has this top-level shape:

```json
{
  "episode_id": "episode-id",
  "score_details": {
    "event": "submit",
    "success": true,
    "reasons": [
      "accepted_evidence_threshold_met",
      "rejected_evidence_threshold_met",
      "affiliate_disclosure_awareness_present"
    ]
  },
  "bundle": {
    "task_id": "uk_espresso_001",
    "accepted_evidence": [],
    "rejected_evidence": [],
    "pending_evidence": [],
    "cum_reward": 67.5,
    "submitted": true,
    "export_paths": {}
  }
}
```

## Markdown shape

The Markdown export contains:

```text
task ID
submission status
cumulative reward
success status
score reasons
accepted evidence
rejected evidence
pending evidence, if any
source URLs
text excerpts
rejection reasons
compliance notes
```

## Inspecting the latest bundle

After running:

```bash
scripts/run_baseline_episode.sh
```

inspect the latest export with:

```bash
scripts/show_latest_bundle_export.sh
```

Expected output shape:

```text
json=/tmp/market_research_env/bundles/<episode_id>.json
markdown=/tmp/market_research_env/bundles/<episode_id>.md
episode_id=<episode_id>
task_id=uk_espresso_001
submitted=True
success=True
cum_reward=67.5
accepted=6
rejected=2
pending=0
```

## Purpose

Bundle exports are the bridge between the evaluation harness and later commercial workflows.

They allow the environment to generate a reviewable artefact without claiming to produce commercial truth automatically. A human reviewer can inspect what evidence was accepted, what was rejected, where it came from, and why the episode scored successfully.
