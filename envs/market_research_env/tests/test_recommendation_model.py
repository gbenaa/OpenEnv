from market_research_env.server.recommendation_model import (
    build_recommendation_summary,
    summary_to_markdown,
)


def test_build_recommendation_summary_from_exported_bundle():
    payload = {
        "episode_id": "episode_test",
        "task_id": "uk_espresso_001",
        "accepted_evidence": [
            {
                "evidence_id": "ev_price",
                "claim": "BrewStart Compact 15 Bar is listed at £149.",
                "claim_type": "price",
                "source_url": "http://127.0.0.1:1234/product_a.html",
                "freshness": "current",
                "reliability": "controlled_local_page",
                "rationale": "Current product price signal.",
                "status": "accepted",
                "extracted_text_excerpt": "Availability: In stock for UK delivery.",
            },
            {
                "evidence_id": "ev_affiliate",
                "claim": "Affiliate buying guides must disclose commission.",
                "claim_type": "affiliate",
                "source_url": "http://127.0.0.1:1234/affiliate_terms.html",
                "freshness": "current",
                "reliability": "controlled_local_page",
                "rationale": "Compliance evidence.",
                "status": "accepted",
                "compliance_notes": "Affiliate disclosure awareness present.",
                "extracted_text_excerpt": "Disclosure expectations.",
            },
        ],
        "rejected_evidence": [
            {
                "evidence_id": "ev_stale",
                "claim": "BrewStart Compact was £79 in a 2022 flash sale.",
                "claim_type": "price",
                "source_url": "http://127.0.0.1:1234/stale_price_page.html",
                "status": "rejected",
            }
        ],
        "pending_evidence": [],
        "cum_reward": 67.5,
        "submitted": True,
    }

    summary = build_recommendation_summary(payload)

    assert summary.task_id == "uk_espresso_001"
    assert summary.source_count == 3
    assert len(summary.product_signals) == 1
    assert summary.product_signals[0].product_name == "BrewStart Compact 15 Bar"
    assert summary.product_signals[0].price_observed == "£149"
    assert summary.product_signals[0].availability == "in stock"
    assert summary.compliance_notes == ["Affiliate disclosure awareness present."]
    assert summary.rejected_claims == ["BrewStart Compact was £79 in a 2022 flash sale."]


def test_recommendation_summary_accepts_nested_bundle_shape():
    payload = {
        "episode_id": "episode_test",
        "bundle": {
            "task_id": "uk_espresso_001",
            "accepted_evidence": [
                {
                    "evidence_id": "ev_product",
                    "claim": "BaristaLite Mini is listed at £179.",
                    "claim_type": "product",
                    "source_url": "http://127.0.0.1:1234/product_c.html",
                    "freshness": "current",
                    "reliability": "controlled_local_page",
                    "rationale": "Candidate product.",
                    "status": "accepted",
                    "extracted_text_excerpt": "Availability: In stock.",
                }
            ],
            "rejected_evidence": [],
            "pending_evidence": [],
        },
    }

    summary = build_recommendation_summary(payload)

    assert summary.task_id == "uk_espresso_001"
    assert len(summary.product_signals) == 1
    assert summary.product_signals[0].product_name == "BaristaLite Mini"


def test_recommendation_summary_renders_markdown():
    summary = build_recommendation_summary(
        {
            "task_id": "uk_espresso_001",
            "accepted_evidence": [
                {
                    "evidence_id": "ev_price",
                    "claim": "CremaGo Manual Espresso is listed at £119.",
                    "claim_type": "price",
                    "source_url": "http://127.0.0.1:1234/product_b.html",
                    "freshness": "current",
                    "reliability": "controlled_local_page",
                    "status": "accepted",
                }
            ],
            "rejected_evidence": [],
        }
    )

    markdown = summary_to_markdown(summary)

    assert "# Recommendation Evidence Summary" in markdown
    assert "CremaGo Manual Espresso" in markdown
    assert "£119" in markdown
