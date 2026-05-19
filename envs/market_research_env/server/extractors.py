"""Lightweight extraction helpers for market-research pages."""

from __future__ import annotations

import re


def clean_text(value: str) -> str:
    """Collapse whitespace for stable observations."""
    return re.sub(r"\s+", " ", value or "").strip()


def excerpt(value: str, max_length: int = 800) -> str:
    """Return a compact excerpt for evidence provenance."""
    value = clean_text(value)
    if len(value) <= max_length:
        return value
    return value[: max_length - 3] + "..."
