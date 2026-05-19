"""FastAPI app for the market research environment."""

from __future__ import annotations

import os
from functools import partial

from openenv.core.env_server.http_server import create_app

from market_research_env.models import MarketResearchAction, MarketResearchObservation
from market_research_env.server.market_research_environment import MarketResearchEnvironment


task_id = os.environ.get("MARKET_RESEARCH_TASK_ID", "uk_espresso_001")
headless = os.environ.get("MARKET_RESEARCH_HEADLESS", "true").lower() == "true"
max_steps = int(os.environ.get("MARKET_RESEARCH_MAX_STEPS", "50"))
port = int(os.environ.get("MARKET_RESEARCH_PORT", "8000"))
max_concurrent = int(os.environ.get("MAX_CONCURRENT_ENVS", "4"))


app = create_app(
    partial(
        MarketResearchEnvironment,
        task_id=task_id,
        headless=headless,
        max_steps=max_steps,
    ),
    MarketResearchAction,
    MarketResearchObservation,
    env_name="market_research_env",
    max_concurrent_envs=max_concurrent,
)


def main() -> None:
    """Run the FastAPI server."""
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
