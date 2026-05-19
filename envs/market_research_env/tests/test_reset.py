from market_research_env.models import MarketResearchState


def test_state_defaults():
    state = MarketResearchState(task_id="uk_espresso_001")

    assert state.task_id == "uk_espresso_001"
    assert state.accepted_count == 0
    assert state.rejected_count == 0
