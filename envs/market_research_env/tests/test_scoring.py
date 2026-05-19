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


def test_duplicate_accepted_evidence_penalised_at_submission():
    scorer = MarketResearchScorer()
    records = [
        EvidenceRecord(
            evidence_id="ev_one",
            claim="Product A is listed at £149.",
            claim_type="price",
            source_url="http://127.0.0.1:1234/product_a.html",
            rationale="Current product price signal.",
        ),
        EvidenceRecord(
            evidence_id="ev_two",
            claim="Product A is listed at £149.",
            claim_type="price",
            source_url="http://127.0.0.1:5678/product_a.html",
            rationale="Repeated current product price signal.",
        ),
    ]

    score, success, details = scorer.score_submit(
        accepted_count=5,
        rejected_count=2,
        has_affiliate_awareness=True,
        minimum_accepted=5,
        minimum_rejected=2,
        disallowed_visit_count=0,
        accepted_records=records,
    )

    assert not success
    assert score == 8.0
    assert details["duplicate_accepted_count"] == 1
    assert "duplicate_accepted_evidence" in details["reasons"]


def test_weak_accepted_evidence_penalised_at_submission():
    scorer = MarketResearchScorer()
    records = [
        EvidenceRecord(
            evidence_id="ev_weak",
            claim="Product A is good.",
            claim_type="product",
            source_url="http://127.0.0.1:1234/product_a.html",
            rationale="",
        ),
    ]

    score, success, details = scorer.score_submit(
        accepted_count=5,
        rejected_count=2,
        has_affiliate_awareness=True,
        minimum_accepted=5,
        minimum_rejected=2,
        disallowed_visit_count=0,
        accepted_records=records,
    )

    assert not success
    assert score == 9.0
    assert details["weak_accepted_count"] == 1
    assert "weak_accepted_evidence" in details["reasons"]
