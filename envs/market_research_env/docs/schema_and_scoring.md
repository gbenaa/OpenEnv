# Market Research Environment Schema and Scoring

## Purpose

This document defines the first stable schema for the market research environment.

The environment is intended to evaluate agentic market-research behaviour, not to automate affiliate marketing directly. It rewards evidence quality, source criticism, provenance, freshness, user usefulness, and compliance awareness.

## Current prototype

The first working task is:

```text
uk_espresso_001
```

The current controlled mini-web supports evidence gathering for a UK budget espresso machine buying-guide assessment.

The current successful baseline produces:

```text
accepted evidence: 6
rejected evidence: 2
pending evidence: 0
submitted: true
success: true
cumulative reward: 55.0
```

## Episode shape

Each episode has these stages:

1. Load a bounded commercial research task.
2. Open the controlled local mini-web.
3. Allow the agent to navigate and inspect pages.
4. Allow the agent to capture evidence.
5. Allow the agent to accept or reject captured evidence.
6. Submit a final evidence bundle.
7. Score the bundle and write trajectory logs.

## Task schema

Each task file should include:

```json
{
  "task_id": "uk_espresso_001",
  "market": "UK",
  "category": "budget espresso machines",
  "objective": "Assess whether there is enough reliable evidence to support a UK affiliate buying guide.",
  "required_signals": [
    "product candidates",
    "price range",
    "review themes",
    "competitor activity",
    "affiliate suitability",
    "user risks"
  ],
  "success_condition": "Submit at least 5 accepted evidence items and at least 2 rejected evidence items with reasons.",
  "minimum_accepted_evidence": 5,
  "minimum_rejected_evidence": 2,
  "requires_affiliate_disclosure_awareness": true,
  "start_path": "/index.html",
  "max_steps": 50
}
```

## Action schema

Supported action types:

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

Browser actions affect page state.

Evidence actions affect the evidence store.

Submission actions produce the final bundle and terminal score.

## Evidence schema

Each captured evidence item should preserve:

```json
{
  "evidence_id": "ev_example",
  "claim": "Product A is listed at £149.",
  "claim_type": "price",
  "source_url": "http://127.0.0.1:12345/product_a.html",
  "observed_at": "2026-05-19T14:29:49Z",
  "source_type": "controlled_local_page",
  "rationale": "Current price signal for a candidate product.",
  "status": "accepted",
  "rejection_reason": "",
  "reliability": "controlled_local_page",
  "freshness": "current",
  "commercial_usefulness": "unknown",
  "user_usefulness": "unknown",
  "compliance_notes": "",
  "extracted_text_excerpt": "Relevant source-page excerpt."
}
```

## Claim types

Recommended initial claim types:

```text
product
price
review
risk
competitor
affiliate
compliance
general
```

## Reward principles

Rewards should favour:

```text
relevance
freshness
provenance
reliability
commercial usefulness
user usefulness
source criticism
compliance awareness
```

Rewards should penalise:

```text
stale prices accepted as current
unsupported commercial claims accepted as reliable
missing source URLs
weak rationales
disallowed external URL visits
submission without affiliate-disclosure awareness
```

## Current scoring summary

Capture rewards:

```text
+0.5 claim present
+0.5 source URL present
+1.0 relevant claim type
+0.5 rationale present
```

Acceptance rewards and penalties:

```text
+2.0 accepted relevant evidence
+1.0 provenance preserved
-3.0 accepted stale or archived evidence
-3.0 accepted unsupported or misleading claim
```

Rejection rewards:

```text
+0.5 base rejection
+2.0 correctly rejected stale evidence
+2.0 correctly rejected unsupported claim
+1.0 rejection reason present
```

Submission rewards and penalties:

```text
+5.0 accepted evidence threshold met
+3.0 rejected evidence threshold met
+2.0 affiliate-disclosure awareness present
-2.0 accepted evidence threshold not met
-2.0 rejected evidence threshold not met
-5.0 affiliate-disclosure awareness missing
-5.0 per disallowed external URL visit
```

## Current success condition

The first task succeeds when:

```text
accepted evidence count >= 5
rejected evidence count >= 2
affiliate-disclosure awareness is present
no disallowed external URL has been visited
```

## Current source policy

The first prototype deliberately uses controlled local pages. It should not depend on:

```text
live retailer scraping
live Google searches
paid SEO tools
paid SERP APIs
affiliate API integration
conversion tracking
automated publishing
```

Later work may add cached pages, manual snapshots, or optional live authorised sources, but those should be separated from deterministic local tests.

## Next schema improvements

Likely next improvements:

1. Add explicit duplicate-evidence detection.
2. Add source-type weighting.
3. Add freshness classification beyond string matching.
4. Add benchmark summary output across repeated runs.
5. Add a second task to test generality.
