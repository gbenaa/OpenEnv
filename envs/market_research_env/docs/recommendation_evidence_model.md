# Recommendation Evidence Model

## Purpose

The market research environment already captures accepted and rejected evidence. This document defines the first recommendation-facing view over that evidence.

The aim is not to generate buying-guide copy automatically. The aim is to convert an evidence bundle into a more useful review structure for a human researcher or downstream evaluator.

## Recommendation-facing fields

A product recommendation signal should preserve:

```text
product_name
price_observed
availability
pros
cons
target_user
risk_notes
source_urls
source_confidence
recommendation_relevance
evidence_ids
```

These fields help distinguish a raw evidence claim from a product recommendation candidate.

## Summary fields

A recommendation evidence summary includes:

```text
task_id
product_signals
risk_notes
compliance_notes
rejected_claims
source_count
```

This keeps the human-facing review grounded in both accepted and rejected evidence.

## Current implementation

The first implementation is intentionally conservative.

It reads an exported evidence bundle and derives product signals for the controlled espresso task. It recognises the local prototype products:

```text
BrewStart Compact 15 Bar
CremaGo Manual Espresso
BaristaLite Mini
```

It extracts price strings such as `£149`, preserves source URLs and evidence IDs, carries across compliance notes, and lists rejected claims.

## How to run

After running a baseline episode and exporting a bundle:

```bash
cd envs/market_research_env
source .venv/bin/activate

scripts/run_baseline_episode.sh
scripts/show_latest_recommendation_summary.sh
```

## Current limits

This is still a deterministic helper, not a general product-recommendation engine.

Known limits:

1. Product recognition is rule-based.
2. It is tuned to the current controlled local pages.
3. It does not yet rank products.
4. It does not yet produce recommendation copy.
5. It does not replace human review.

## Next improvements

Likely next steps:

1. Add target-user classification.
2. Add explicit pros and cons extraction.
3. Add product ranking criteria.
4. Support multiple task categories.
5. Emit a Markdown review sheet for human approval.
