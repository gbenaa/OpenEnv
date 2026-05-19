import pytest

from market_research_env.models import MarketResearchAction
from market_research_env.server.market_research_environment import MarketResearchEnvironment


@pytest.mark.integration
def test_air_fryer_task_starts_on_own_local_web_pages():
    env = MarketResearchEnvironment(task_id="uk_air_fryers_001", headless=True)

    try:
        obs = env.reset()

        assert obs.task["task_id"] == "uk_air_fryers_001"
        assert obs.task["category"] == "budget air fryers"
        assert "budget air fryers" in obs.page_text.lower()
        assert "/air_fryers/index.html" in obs.url

        obs = env.step(MarketResearchAction(action_type="extract_links"))

        hrefs = {link["href"] for link in obs.links}
        assert any("/air_fryers/search.html" in href for href in hrefs)
        assert any("/air_fryers/affiliate_terms.html" in href for href in hrefs)
        assert any("/air_fryers/stale_price_page.html" in href for href in hrefs)
        assert any("/air_fryers/misleading_claim_page.html" in href for href in hrefs)

    finally:
        env.close()
