"""Run the scripted market-research baseline in process.

This runner does not require starting the FastAPI server. It instantiates the
environment directly, opens the controlled local mini-web through BrowserGym,
captures evidence, submits the bundle, and prints a concise result summary.
"""

from __future__ import annotations

from typing import Any

from market_research_env.models import MarketResearchAction
from market_research_env.server.market_research_environment import MarketResearchEnvironment


def capture_and_accept(
    env: MarketResearchEnvironment,
    claim: str,
    claim_type: str,
    rationale: str,
    **kwargs: Any,
):
    """Capture an evidence item and immediately accept it."""
    obs = env.step(
        MarketResearchAction(
            action_type="capture_evidence",
            claim=claim,
            claim_type=claim_type,
            rationale=rationale,
            **kwargs,
        )
    )
    evidence_id = obs.pending_evidence[-1].evidence_id
    return env.step(
        MarketResearchAction(
            action_type="accept_evidence",
            evidence_id=evidence_id,
        )
    )


def capture_and_reject(
    env: MarketResearchEnvironment,
    claim: str,
    claim_type: str,
    rationale: str,
    reason: str,
    **kwargs: Any,
):
    """Capture an evidence item and immediately reject it with a reason."""
    obs = env.step(
        MarketResearchAction(
            action_type="capture_evidence",
            claim=claim,
            claim_type=claim_type,
            rationale=rationale,
            **kwargs,
        )
    )
    evidence_id = obs.pending_evidence[-1].evidence_id
    return env.step(
        MarketResearchAction(
            action_type="reject_evidence",
            evidence_id=evidence_id,
            rejection_reason=reason,
        )
    )


def main() -> None:
    """Run the baseline episode and print a compact success summary."""
    env = MarketResearchEnvironment(headless=True)

    try:
        env.reset()

        env.step(MarketResearchAction(action_type="goto", url="/product_a.html"))
        capture_and_accept(
            env,
            "BrewStart Compact 15 Bar is listed at £149.",
            "price",
            "Current product price signal from controlled product page.",
            freshness="current",
            reliability="controlled_local_page",
        )

        env.step(MarketResearchAction(action_type="goto", url="/product_b.html"))
        capture_and_accept(
            env,
            "CremaGo Manual Espresso is listed at £119 with limited stock.",
            "price",
            "Current price and availability signal.",
            freshness="current",
            reliability="controlled_local_page",
        )

        env.step(MarketResearchAction(action_type="goto", url="/product_c.html"))
        capture_and_accept(
            env,
            "BaristaLite Mini is listed at £179 and positioned as an easy-cleaning budget option.",
            "product",
            "Product candidate and positioning evidence.",
            freshness="current",
            reliability="controlled_local_page",
        )

        env.step(MarketResearchAction(action_type="goto", url="/competitor_review_1.html"))
        capture_and_accept(
            env,
            "Competitor review themes include value, cleaning effort, milk steaming quality, and beginner friendliness.",
            "competitor",
            "Competitor-positioning evidence for the buying guide.",
            freshness="current",
            reliability="controlled_local_page",
        )

        env.step(MarketResearchAction(action_type="goto", url="/competitor_review_2.html"))
        capture_and_accept(
            env,
            "User-risk themes include weak steam pressure, inconsistent temperature, noisy pumps, and grinder expectations.",
            "risk",
            "User-centred risk evidence for recommendation quality.",
            freshness="current",
            reliability="controlled_local_page",
        )

        env.step(MarketResearchAction(action_type="goto", url="/affiliate_terms.html"))
        capture_and_accept(
            env,
            "Affiliate buying guides must disclose commission and note that prices and availability may change.",
            "affiliate",
            "Compliance evidence for affiliate-disclosure awareness.",
            freshness="current",
            reliability="controlled_local_page",
            compliance_notes="Affiliate disclosure awareness present.",
        )

        env.step(MarketResearchAction(action_type="goto", url="/stale_price_page.html"))
        capture_and_reject(
            env,
            "BrewStart Compact was £79 in a 2022 flash sale.",
            "price",
            "Archived price claim is stale and not current price evidence.",
            "Stale archived price from 2022 should not be accepted as current.",
            freshness="stale",
        )

        env.step(MarketResearchAction(action_type="goto", url="/misleading_claim_page.html"))
        capture_and_reject(
            env,
            "A £99 machine makes professional cafe-quality espresso for every user with no grinder, no skill, and no maintenance.",
            "review",
            "Unsupported sales claim with no tests or source data.",
            "Unsupported and misleading claim.",
            reliability="unsupported",
        )

        obs = env.step(MarketResearchAction(action_type="submit_bundle"))

        accepted_count = len(obs.evidence_bundle["accepted_evidence"])
        rejected_count = len(obs.evidence_bundle["rejected_evidence"])
        cum_reward = obs.evidence_bundle["cum_reward"]

        print(f"done={obs.done}")
        print(f"success={obs.score_details.get('success')}")
        print(f"accepted={accepted_count}")
        print(f"rejected={rejected_count}")
        print(f"cum_reward={cum_reward}")
        print(f"reasons={obs.score_details.get('reasons')}")

        if not obs.done or not obs.score_details.get("success"):
            raise SystemExit(1)

    finally:
        env.close()


if __name__ == "__main__":
    main()
