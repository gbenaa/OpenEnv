"""Compliance checks for the market-research environment."""

from __future__ import annotations

from urllib.parse import urljoin, urlparse


class ComplianceChecker:
    """Check URLs and evidence-bundle compliance signals."""

    def __init__(self, base_url: str, allowed_prefixes: list[str] | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.allowed_prefixes = allowed_prefixes or [
            "http://localhost",
            "http://127.0.0.1",
            self.base_url,
        ]

    def normalise_url(self, url: str | None) -> str:
        if not url:
            return self.base_url + "/index.html"
        if url.startswith("/"):
            return urljoin(self.base_url + "/", url.lstrip("/"))
        if not urlparse(url).scheme:
            return urljoin(self.base_url + "/", url)
        return url

    def is_allowed_url(self, url: str) -> bool:
        return any(url.startswith(prefix) for prefix in self.allowed_prefixes)

    def affiliate_awareness_present(self, text_values: list[str]) -> bool:
        combined = " ".join(value.lower() for value in text_values)
        markers = [
            "affiliate",
            "commission",
            "qualifying purchases",
            "prices and availability",
            "disclose",
            "disclosure",
        ]
        return any(marker in combined for marker in markers)
