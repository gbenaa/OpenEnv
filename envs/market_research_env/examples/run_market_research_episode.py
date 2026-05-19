"""Run a minimal market-research episode against a running server."""

from __future__ import annotations

import asyncio

from market_research_env import MarketResearchAction, MarketResearchEnv


async def main() -> None:
    async with MarketResearchEnv(base_url="http://localhost:8000") as env:
        result = await env.reset()
        print(result.observation.message)
        print(result.observation.task.get("objective", ""))

        result = await env.step(MarketResearchAction(action_type="extract_links"))
        for link in result.observation.links:
            print(f"{link['text']} -> {link['href']}")


if __name__ == "__main__":
    asyncio.run(main())
