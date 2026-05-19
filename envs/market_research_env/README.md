---
title: Market Research Environment Server
emoji: ""
colorFrom: blue
colorTo: gray
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
  - browsergym
  - market-research
  - evidence-evaluation
---

# Market Research Environment

This environment is a first controlled OpenEnv prototype for repeatable agentic market-research workflows.

It is not an affiliate-marketing automation tool. It is a browser-based evaluation harness for testing whether agents can gather, criticise, accept, reject, and bundle commercial evidence under explicit constraints.

## Purpose

The first prototype supports a local commercial mini-web and one bounded task:

```text
uk_espresso_001
```

The task asks an agent to assess whether there is enough reliable evidence to support a UK affiliate buying guide on budget espresso machines.

## What this environment demonstrates

The environment turns market-research behaviour into a reproducible OpenEnv episode:

1. The agent receives a bounded commercial research task.
2. The agent browses a controlled local mini-web.
3. The agent extracts product, price, review, competitor, affiliate, and user-risk evidence.
4. The agent captures evidence with provenance.
5. The agent accepts or rejects evidence with reasons.
6. The environment scores source criticism, freshness, reliability, usefulness, and compliance.
7. The agent submits a final evidence bundle.
8. The episode records the trajectory and scoring details.

## Why local pages first

The first implementation deliberately avoids:

```text
live retailer scraping
live Google searches
paid SEO tools
paid SERP APIs
affiliate API integration
conversion tracking
automated publishing
```

This keeps the first environment cheap, repeatable, safe, and testable.

## Action model

The action model is structured rather than a single raw browser-action string.

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

Browser actions are translated internally into Playwright or BrowserGym operations. Evidence actions are first-class because evidence quality is what the environment evaluates.

## Quick start

From the repository root:

```bash
cd envs/market_research_env
pip install -e .
playwright install chromium
python -m market_research_env.server.app
```

In another terminal:

```python
import asyncio
from market_research_env import MarketResearchAction, MarketResearchEnv

async def main():
    async with MarketResearchEnv(base_url="http://localhost:8000") as env:
        result = await env.reset()
        print(result.observation.message)
        print(result.observation.page_text[:500])

        result = await env.step(MarketResearchAction(action_type="extract_links"))
        print(result.observation.links)

asyncio.run(main())
```

## Docker

From the environment directory:

```bash
cd envs/market_research_env
docker build -t market-research-env:latest -f server/Dockerfile .
docker run --rm -p 8000:8000 market-research-env:latest
```

## Local mini-web

The local mini-web is in:

```text
local_web/
```

It includes:

```text
index.html
search.html
product_a.html
product_b.html
product_c.html
competitor_review_1.html
competitor_review_2.html
affiliate_terms.html
stale_price_page.html
misleading_claim_page.html
```

The stale and misleading pages exist so that an agent can be rewarded for rejecting weak or non-compliant evidence.

## Task success condition

The first task requires:

```text
at least 5 accepted evidence items
at least 2 rejected evidence items
affiliate-disclosure awareness
no disallowed external URLs
```

The environment gives rewards for relevant evidence and source criticism, and penalties for stale, unsupported, duplicated, or non-compliant claims.

## Development tests

The environment has local test runners so fast tests and browser-backed integration tests can be run separately.

From the environment directory:

```bash
cd envs/market_research_env
source .venv/bin/activate

scripts/run_fast_tests.sh
scripts/run_integration_tests.sh
scripts/run_all_tests.sh
```

The fast tests cover deterministic scoring, evidence storage, compliance, and local helper behaviour.

The integration tests run the browser-backed scripted baseline episode using BrowserGym and Playwright.
## Evidence bundle exports

After a submitted episode, JSON and Markdown evidence bundles are written under:

```text
/tmp/market_research_env/bundles/
```

Run the baseline and inspect the latest export with:

```bash
scripts/run_baseline_episode.sh
scripts/show_latest_bundle_export.sh
```

See `docs/evidence_bundle_exports.md` for the export schema and review format.

