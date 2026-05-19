from market_research_env.server.compliance import ComplianceChecker


def test_affiliate_awareness_detection():
    checker = ComplianceChecker("http://127.0.0.1:1234")

    assert checker.affiliate_awareness_present([
        "Buying guides must disclose affiliate commission.",
    ])
