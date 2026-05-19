"""Run a negative-control market-research baseline.

The intended conclusion is that the evidence is not sufficient to support a
buying guide. The episode succeeds by accepting disclosure/insufficiency
evidence and rejecting weak, stale, or unsupported claims.
"""

from __future__ import annotations

from market_research_env.models import MarketResearchAction
from market_research_env.server.market_research_environment import MarketResearchEnvironment


def capture_and_accept(env: MarketResearchEnvironment, claim: str, claim_type: str, rationale: str, **kwargs):
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
    return env.step(MarketResearchAction(action_type="accept_evidence", evidence_id=evidence_id))


def capture_and_reject(
    env: MarketResearchEnvironment,
    claim: str,
    claim_type: str,
    rationale: str,
    reason: str,
    **kwargs,
):
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
    env = MarketResearchEnvironment(task_id="uk_smart_rings_negative_001", headless=True)

    try:
        env.reset()

        env.step(MarketResearchAction(action_type="goto", url="/smart_rings_negative/product_claim.html"))
        capture_and_reject(
            env,
            "RingPulse Lite is the best budget smart ring in the UK at £49.",
            "product",
            "The page lacks retailer, stock, test, warranty, and review evidence.",
            "Unsupported product claim should not be accepted as reliable buying-guide evidence.",
            reliability="unsupported",
            freshness="unknown",
        )

        env.step(MarketResearchAction(action_type="goto", url="/smart_rings_negative/forum_warning.html"))
        capture_and_reject(
            env,
            "Forum users report sizing, battery, app-support, returns, and sensor-reliability concerns.",
            "risk",
            "Risk evidence is useful, but it does not establish reliable product recommendations.",
            "Risk discussion alone is insufficient for a buying guide.",
            reliability="partial",
            freshness="current",
        )

        env.step(MarketResearchAction(action_type="goto", url="/smart_rings_negative/stale_review.html"))
        capture_and_reject(
            env,
            "The 2021 SmartLoop Mini is the cheapest worthwhile smart ring.",
            "review",
            "Archived 2021 review is stale.",
            "Stale archived review should not be accepted as current evidence.",
            reliability="unknown",
            freshness="stale",
        )

        env.step(MarketResearchAction(action_type="goto", url="/smart_rings_negative/unsupported_claim.html"))
        capture_and_reject(
            env,
            "This budget ring gives clinical-grade sleep and health tracking for every user.",
            "review",
            "No source data, sensor validation, medical disclaimer, specification, or independent review is supplied.",
            "Unsupported health and sensor claim should be rejected.",
            reliability="unsupported",
            freshness="unknown",
        )

        env.step(MarketResearchAction(action_type="goto", url="/smart_rings_negative/affiliate_terms.html"))
        capture_and_accept(
            env,
            "Affiliate buying guides must disclose commission and avoid recommending products when evidence is weak, stale, or unsupported.",
            "affiliate",
            "This supports the negative-control conclusion and shows affiliate-disclosure awareness.",
            reliability="controlled_local_page",
            freshness="current",
            compliance_notes="Affiliate disclosure awareness present; evidence is insufficient for recommendation.",
        )

        obs = env.step(MarketResearchAction(action_type="submit_bundle"))

        print(f"done={obs.done}")
        print(f"success={obs.score_details.get('success')}")
        print("expected_conclusion=insufficient_evidence")
        print(f"accepted={len(obs.evidence_bundle['accepted_evidence'])}")
        print(f"rejected={len(obs.evidence_bundle['rejected_evidence'])}")
        print(f"cum_reward={obs.evidence_bundle['cum_reward']}")
        print(f"reasons={obs.score_details.get('reasons')}")

    finally:
        env.close()


if __name__ == "__main__":
    main()
