from market_research_env.server.compliance import ComplianceChecker


def test_normalise_relative_url():
    checker = ComplianceChecker("http://127.0.0.1:1234")

    assert checker.normalise_url("/product_a.html") == "http://127.0.0.1:1234/product_a.html"


def test_external_url_not_allowed():
    checker = ComplianceChecker("http://127.0.0.1:1234")

    assert checker.is_allowed_url("https://example.com/product") is False
