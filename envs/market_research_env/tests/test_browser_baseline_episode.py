import pytest

from market_research_env.models import MarketResearchAction
from market_research_env.server.market_research_environment import MarketResearchEnvironment


@pytest.mark.integration
def test_scripted_browser_baseline_episode():
    env = MarketResearchEnvironment(headless=True)

    try:
        obs = env.reset()
        assert "budget espresso machines" in obs.task["category"]

        def capture_and_accept(claim, claim_type, rationale, **kwargs):
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

        def capture_and_reject(claim, claim_type, rationale, reason, **kwargs):
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

        env.step(MarketResearchAction(action_type="goto", url="/product_a.html"))
        capture_and_accept(
            "BrewStart Compact 15 Bar is listed at £149.",
            "price",
            "Current product price signal from controlled product page.",
            freshness="current",
            reliability="controlled_local_page",
        )

        env.step(MarketResearchAction(action_type="goto", url="/product_b.html"))
        capture_and_accept(
            "CremaGo Manual Espresso is listed at £119 with limited stock.",
            "price",
            "Current price and availability signal.",
            freshness="current",
            reliability="controlled_local_page",
        )

        env.step(MarketResearchAction(action_type="goto", url="/product_c.html"))
        capture_and_accept(
            "BaristaLite Mini is listed at £179 and positioned as an easy-cleaning budget option.",
            "product",
            "Product candidate and positioning evidence.",
            freshness="current",
            reliability="controlled_local_page",
        )

        env.step(MarketResearchAction(action_type="goto", url="/competitor_review_1.html"))
        capture_and_accept(
            "Competitor review themes include value, cleaning effort, milk steaming quality, and beginner friendliness.",
            "competitor",
            "Competitor-positioning evidence for the buying guide.",
            freshness="current",
            reliability="controlled_local_page",
        )

        env.step(MarketResearchAction(action_type="goto", url="/competitor_review_2.html"))
        capture_and_accept(
            "User-risk themes include weak steam pressure, inconsistent temperature, noisy pumps, and grinder expectations.",
            "risk",
            "User-centred risk evidence for recommendation quality.",
            freshness="current",
            reliability="controlled_local_page",
        )

        env.step(MarketResearchAction(action_type="goto", url="/affiliate_terms.html"))
        capture_and_accept(
            "Affiliate buying guides must disclose commission and note that prices and availability may change.",
            "affiliate",
            "Compliance evidence for affiliate-disclosure awareness.",
            freshness="current",
            reliability="controlled_local_page",
            compliance_notes="Affiliate disclosure awareness present.",
        )

        env.step(MarketResearchAction(action_type="goto", url="/stale_price_page.html"))
        capture_and_reject(
            "BrewStart Compact was £79 in a 2022 flash sale.",
            "price",
            "Archived price claim is stale and not current price evidence.",
            "Stale archived price from 2022 should not be accepted as current.",
            freshness="stale",
        )

        env.step(MarketResearchAction(action_type="goto", url="/misleading_claim_page.html"))
        capture_and_reject(
            "A £99 machine makes professional cafe-quality espresso for every user with no grinder, no skill, and no maintenance.",
            "review",
            "Unsupported sales claim with no tests or source data.",
            "Unsupported and misleading claim.",
            reliability="unsupported",
        )

        obs = env.step(MarketResearchAction(action_type="submit_bundle"))

        assert obs.done is True
        assert obs.score_details["success"] is True
        assert obs.evidence_bundle["submitted"] is True
        assert len(obs.evidence_bundle["accepted_evidence"]) >= 5
        assert len(obs.evidence_bundle["rejected_evidence"]) >= 2
        assert obs.evidence_bundle["cum_reward"] > 0

    finally:
        env.close()
