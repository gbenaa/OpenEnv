from market_research_env.examples.run_strategy_benchmark import StrategyRunResult, summarise_results


def test_strategy_summary_separates_good_and_bad_results():
    results = [
        StrategyRunResult(
            strategy="successful_baseline",
            run_index=1,
            success=True,
            reward=67.5,
            accepted=6,
            rejected=2,
            pending=0,
            reasons=["accepted_evidence_threshold_met"],
        ),
        StrategyRunResult(
            strategy="no_disclosure",
            run_index=1,
            success=False,
            reward=50.0,
            accepted=5,
            rejected=2,
            pending=0,
            reasons=["affiliate_disclosure_awareness_missing"],
        ),
    ]

    summary = summarise_results(results)

    assert summary["strategies"]["successful_baseline"]["success_rate"] == 1.0
    assert summary["strategies"]["no_disclosure"]["success_rate"] == 0.0
    assert summary["strategies"]["successful_baseline"]["mean_reward"] == 67.5
