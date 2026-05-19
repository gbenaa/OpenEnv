from market_research_env.models import EvidenceRecord
from market_research_env.server.scorer import MarketResearchScorer


def test_rejecting_stale_evidence_scores_positive():
    scorer = MarketResearchScorer()
    record = EvidenceRecord(
        evidence_id="ev_test",
        claim="Archived 2022 price claim",
        claim_type="price",
        source_url="http://localhost/stale_price_page.html",
        rejection_reason="Stale archived price",
    )

    score, details = scorer.score_reject(record)

    assert score > 0
    assert "correctly_rejected_stale_evidence" in details["reasons"]


def test_submit_requires_affiliate_awareness():
    scorer = MarketResearchScorer()

    score, success, details = scorer.score_submit(
        accepted_count=5,
        rejected_count=2,
        has_affiliate_awareness=False,
        minimum_accepted=5,
        minimum_rejected=2,
        disallowed_visit_count=0,
    )

    assert not success
    assert score < 10
    assert "affiliate_disclosure_awareness_missing" in details["reasons"]
