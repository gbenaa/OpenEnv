"""Client for the OpenEnv market research environment."""

from __future__ import annotations

from typing import Any

from openenv.core.client_types import StepResult
from openenv.core.env_client import EnvClient

from .models import (
    EvidenceRecord,
    MarketResearchAction,
    MarketResearchObservation,
    MarketResearchState,
)


class MarketResearchEnv(
    EnvClient[MarketResearchAction, MarketResearchObservation, MarketResearchState]
):
    """Client for interacting with the market research environment."""

    def _step_payload(self, action: MarketResearchAction) -> dict[str, Any]:
        return action.model_dump()

    def _parse_result(
        self, payload: dict[str, Any]
    ) -> StepResult[MarketResearchObservation]:
        obs_data = payload.get("observation", {})

        observation = MarketResearchObservation(
            message=obs_data.get("message", ""),
            task=obs_data.get("task", {}),
            url=obs_data.get("url", ""),
            page_text=obs_data.get("page_text", ""),
            links=obs_data.get("links", []),
            pending_evidence=[
                EvidenceRecord(**item) for item in obs_data.get("pending_evidence", [])
            ],
            accepted_evidence=[
                EvidenceRecord(**item) for item in obs_data.get("accepted_evidence", [])
            ],
            rejected_evidence=[
                EvidenceRecord(**item) for item in obs_data.get("rejected_evidence", [])
            ],
            evidence_bundle=obs_data.get("evidence_bundle", {}),
            last_action_error=obs_data.get("last_action_error"),
            score_details=obs_data.get("score_details", {}),
            done=payload.get("done", False),
            reward=payload.get("reward"),
            metadata=obs_data.get("metadata", {}),
        )

        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: dict[str, Any]) -> MarketResearchState:
        return MarketResearchState(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
            task_id=payload.get("task_id", ""),
            current_url=payload.get("current_url", ""),
            accepted_count=payload.get("accepted_count", 0),
            rejected_count=payload.get("rejected_count", 0),
            pending_count=payload.get("pending_count", 0),
            submitted=payload.get("submitted", False),
            max_steps=payload.get("max_steps", 50),
            cum_reward=payload.get("cum_reward", 0.0),
            disallowed_visit_count=payload.get("disallowed_visit_count", 0),
        )
