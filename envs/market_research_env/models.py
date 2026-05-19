"""Data models for the OpenEnv market research environment."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

try:
    from openenv.core.env_server.types import Action, Observation, State
except ImportError:
    from openenv_core.env_server.types import Action, Observation, State


EvidenceStatus = Literal["pending", "accepted", "rejected"]
ActionType = Literal[
    "goto",
    "click",
    "fill",
    "scroll",
    "extract_page_text",
    "extract_links",
    "capture_evidence",
    "accept_evidence",
    "reject_evidence",
    "submit_bundle",
    "noop",
]


class EvidenceRecord(Observation):
    """A single captured market-research evidence item."""

    evidence_id: str = Field(default="", description="Stable ID for this evidence item")
    claim: str = Field(default="", description="The specific market-relevant claim")
    claim_type: str = Field(
        default="general",
        description="Evidence type such as product, price, review, risk, competitor, affiliate, compliance",
    )
    source_url: str = Field(default="", description="URL from which the evidence was observed")
    observed_at: str = Field(default="", description="UTC timestamp for the observation")
    source_type: str = Field(default="controlled_local_page")
    rationale: str = Field(default="", description="Why the item is relevant")
    status: EvidenceStatus = Field(default="pending")
    rejection_reason: str = Field(default="")
    reliability: str = Field(default="unknown")
    freshness: str = Field(default="unknown")
    commercial_usefulness: str = Field(default="unknown")
    user_usefulness: str = Field(default="unknown")
    compliance_notes: str = Field(default="")
    extracted_text_excerpt: str = Field(default="")
    metadata: dict[str, Any] = Field(default_factory=dict)


class MarketResearchAction(Action):
    """Structured action for browser and evidence operations."""

    action_type: ActionType = Field(..., description="Action to perform")

    # = Browser fields
    # -> Use selector for direct Playwright access, or bid for BrowserGym-style accessibility IDs.
    selector: str | None = Field(default=None)
    bid: str | None = Field(default=None)
    text: str | None = Field(default=None)
    url: str | None = Field(default=None)
    direction: Literal["up", "down"] | None = Field(default=None)

    # = Evidence fields
    # -> These fields are used by capture, accept, reject, and submit actions.
    evidence_id: str | None = Field(default=None)
    claim: str | None = Field(default=None)
    claim_type: str | None = Field(default=None)
    rationale: str | None = Field(default=None)
    rejection_reason: str | None = Field(default=None)
    reliability: str | None = Field(default=None)
    freshness: str | None = Field(default=None)
    commercial_usefulness: str | None = Field(default=None)
    user_usefulness: str | None = Field(default=None)
    compliance_notes: str | None = Field(default=None)

    # = General metadata
    # -> Agents can attach structured notes that are preserved in trajectory logs.
    action_metadata: dict[str, Any] = Field(default_factory=dict)


class MarketResearchObservation(Observation):
    """Observation returned after each market research action."""

    message: str = Field(default="")
    task: dict[str, Any] = Field(default_factory=dict)
    url: str = Field(default="")
    page_text: str = Field(default="")
    links: list[dict[str, str]] = Field(default_factory=list)

    pending_evidence: list[EvidenceRecord] = Field(default_factory=list)
    accepted_evidence: list[EvidenceRecord] = Field(default_factory=list)
    rejected_evidence: list[EvidenceRecord] = Field(default_factory=list)
    evidence_bundle: dict[str, Any] = Field(default_factory=dict)

    last_action_error: str | None = Field(default=None)
    score_details: dict[str, Any] = Field(default_factory=dict)


class MarketResearchState(State):
    """State for a market-research episode."""

    task_id: str = Field(default="")
    current_url: str = Field(default="")
    accepted_count: int = Field(default=0)
    rejected_count: int = Field(default=0)
    pending_count: int = Field(default=0)
    submitted: bool = Field(default=False)
    max_steps: int = Field(default=50)
    cum_reward: float = Field(default=0.0)
    disallowed_visit_count: int = Field(default=0)
