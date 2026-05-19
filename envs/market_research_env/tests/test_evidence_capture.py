from market_research_env.server.evidence_store import EvidenceStore


def test_capture_accept_reject_counts():
    store = EvidenceStore()
    first = store.capture(
        claim="Product A is £149",
        claim_type="price",
        source_url="http://localhost/product_a.html",
    )
    second = store.capture(
        claim="Archived stale price",
        claim_type="price",
        source_url="http://localhost/stale_price_page.html",
    )

    store.accept(first.evidence_id)
    store.reject(second.evidence_id, "Stale")

    assert len(store.accepted()) == 1
    assert len(store.rejected()) == 1
    assert len(store.pending()) == 0
