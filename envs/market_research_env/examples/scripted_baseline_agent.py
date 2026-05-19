"""Scripted baseline for uk_espresso_001.

This is deliberately simple. It demonstrates the intended episode shape rather
than trying to be an intelligent market-research agent.
"""

from __future__ import annotations

import asyncio

from market_research_env import MarketResearchAction, MarketResearchEnv


async def capture_and_accept(env: MarketResearchEnv, claim: str, claim_type: str, rationale: str, **kwargs) -> None:
    result = await env.step(
        MarketResearchAction(
            action_type="capture_evidence",
            claim=claim,
            claim_type=claim_type,
            rationale=rationale,
            **kwargs,
        )
    )
    evidence_id = result.observation.pending_evidence[-1].evidence_id
    await env.step(MarketResearchAction(action_type="accept_evidence", evidence_id=evidence_id))


async def capture_and_reject(env: MarketResearchEnv, claim: str, claim_type: str, rationale: str, reason: str, **kwargs) -> None:
    result = await env.step(
        MarketResearchAction(
            action_type="capture_evidence",
            claim=claim,
            claim_type=claim_type,
            rationale=rationale,
            **kwargs,
        )
    )
    evidence_id = result.observation.pending_evidence[-1].evidence_id
    await env.step(
        MarketResearchAction(
            action_type="reject_evidence",
            evidence_id=evidence_id,
            rejection_reason=reason,
        )
    )


async def main() -> None:
    async with MarketResearchEnv(base_url="http://localhost:8000") as env:
        await env.reset()

        await env.step(MarketResearchAction(action_type="goto", url="/product_a.html"))
        await env.step(MarketResearchAction(action_type="extract_page_text"))
        await capture_and_accept(
            env,
            "BrewStart Compact 15 Bar is listed at £149.",
            "price",
            "Current product price signal from controlled product page.",
            freshness="current",
            reliability="controlled_local_page",
        )

        await env.step(MarketResearchAction(action_type="goto", url="/product_b.html"))
        await capture_and_accept(
            env,
            "CremaGo Manual Espresso is listed at £119 with limited stock.",
            "price",
            "Current price and availability signal.",
            freshness="current",
            reliability="controlled_local_page",
        )

        await env.step(MarketResearchAction(action_type="goto", url="/product_c.html"))
        await capture_and_accept(
            env,
            "BaristaLite Mini is listed at £179 and positioned as an easy-cleaning budget option.",
            "product",
            "Product candidate and positioning evidence.",
            freshness="current",
            reliability="controlled_local_page",
        )

        await env.step(MarketResearchAction(action_type="goto", url="/competitor_review_1.html"))
        await capture_and_accept(
            env,
            "Competitor review themes include value, cleaning effort, milk steaming quality, and beginner friendliness.",
            "competitor",
            "Competitor-positioning evidence for the buying guide.",
            freshness="current",
            reliability="controlled_local_page",
        )

        await env.step(MarketResearchAction(action_type="goto", url="/competitor_review_2.html"))
        await capture_and_accept(
            env,
            "User-risk themes include weak steam pressure, inconsistent temperature, noisy pumps, and grinder expectations.",
            "risk",
            "User-centred risk evidence for recommendation quality.",
            freshness="current",
            reliability="controlled_local_page",
        )

        await env.step(MarketResearchAction(action_type="goto", url="/affiliate_terms.html"))
        await capture_and_accept(
            env,
            "Affiliate buying guides must disclose commission and note that prices and availability may change.",
            "affiliate",
            "Compliance evidence for affiliate-disclosure awareness.",
            freshness="current",
            reliability="controlled_local_page",
            compliance_notes="Affiliate disclosure awareness present.",
        )

        await env.step(MarketResearchAction(action_type="goto", url="/stale_price_page.html"))
        await capture_and_reject(
            env,
            "BrewStart Compact was £79 in a 2022 flash sale.",
            "price",
            "Archived price claim is stale and not current price evidence.",
            "Stale archived price from 2022 should not be accepted as current.",
            freshness="stale",
        )

        await env.step(MarketResearchAction(action_type="goto", url="/misleading_claim_page.html"))
        await capture_and_reject(
            env,
            "A £99 machine makes professional cafe-quality espresso for every user with no grinder, no skill, and no maintenance.",
            "review",
            "Unsupported sales claim with no tests or source data.",
            "Unsupported and misleading claim.",
            reliability="unsupported",
        )

        result = await env.step(MarketResearchAction(action_type="submit_bundle"))
        print(result.reward)
        print(result.done)
        print(result.observation.score_details)
        print(result.observation.evidence_bundle)


if __name__ == "__main__":
    asyncio.run(main())
