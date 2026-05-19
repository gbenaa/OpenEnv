from market_research_env.models import EvidenceRecord
from market_research_env.server.scorer import MarketResearchScorer


def test_accept_current_controlled_evidence_gets_source_and_freshness_reasons():
    scorer = MarketResearchScorer()
    record = EvidenceRecord(
        evidence_id="ev_current",
        claim="Product A is listed at £149.",
        claim_type="price",
        source_url="http://localhost/product_a.html",
        source_type="controlled_local_page",
        rationale="Current product price signal.",
        reliability="controlled_local_page",
        freshness="current",
    )

    score, details = scorer.score_accept(record)

    assert score > 3.0
    assert "source_type_controlled_local_page" in details["reasons"]
    assert "freshness_current" in details["reasons"]
    assert "reliability_controlled_local_page" in details["reasons"]


def test_accepting_stale_price_is_penalised_more_than_current_price():
    scorer = MarketResearchScorer()

    current = EvidenceRecord(
        evidence_id="ev_current",
        claim="Product A is listed at £149.",
        claim_type="price",
        source_url="http://localhost/product_a.html",
        source_type="controlled_local_page",
        rationale="Current product price signal.",
        freshness="current",
        reliability="controlled_local_page",
    )
    stale = EvidenceRecord(
        evidence_id="ev_stale",
        claim="Product A was £79 in a 2022 archived flash sale.",
        claim_type="price",
        source_url="http://localhost/stale_price_page.html",
        source_type="controlled_local_page",
        rationale="Archived price claim.",
        freshness="stale",
    )

    current_score, _ = scorer.score_accept(current)
    stale_score, stale_details = scorer.score_accept(stale)

    assert stale_score < current_score
    assert "accepted_stale_or_archived_evidence" in stale_details["reasons"]


def test_rejecting_stale_freshness_gets_explicit_freshness_reason():
    scorer = MarketResearchScorer()
    record = EvidenceRecord(
        evidence_id="ev_stale",
        claim="Product A was £79 in a 2022 flash sale.",
        claim_type="price",
        source_url="http://localhost/stale_price_page.html",
        rationale="Archived price claim is not current evidence.",
        rejection_reason="Stale archived price from 2022.",
        freshness="stale",
    )

    score, details = scorer.score_reject(record)

    assert score > 3.0
    assert "rejected_freshness_stale" in details["reasons"]


def test_submit_penalises_duplicate_accepted_evidence():
    scorer = MarketResearchScorer()
    records = [
        EvidenceRecord(
            evidence_id="ev_1",
            claim="Product A is listed at £149.",
            claim_type="price",
            source_url="http://localhost/product_a.html",
            rationale="Current price.",
        ),
        EvidenceRecord(
            evidence_id="ev_2",
            claim="Product A is listed at £149.",
            claim_type="price",
            source_url="http://localhost/product_a.html",
            rationale="Current price repeated.",
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
    assert score < 10.0
    assert "duplicate_accepted_evidence" in details["reasons"]


def test_submit_penalises_weak_accepted_evidence():
    scorer = MarketResearchScorer()
    records = [
        EvidenceRecord(
            evidence_id="ev_weak",
            claim="",
            claim_type="general",
            source_url="",
            rationale="",
        )
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
    assert score < 10.0
    assert "weak_accepted_evidence" in details["reasons"]
