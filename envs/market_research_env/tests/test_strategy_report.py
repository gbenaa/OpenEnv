import json
from pathlib import Path

from market_research_env.examples.show_latest_strategy_report import write_report


def test_strategy_report_contains_comparison_table(tmp_path: Path):
    payload = {
        "runs": [
            {
                "strategy": "successful_baseline",
                "success": True,
                "reward": 67.5,
                "accepted": 6,
                "rejected": 2,
            },
            {
                "strategy": "accept_everything",
                "success": False,
                "reward": 50.25,
                "accepted": 8,
                "rejected": 0,
            },
        ]
    }

    source_path = tmp_path / "sample_strategy_benchmark.json"
    source_path.write_text(json.dumps(payload), encoding="utf-8")

    report_path = write_report(source_path)
    report = report_path.read_text(encoding="utf-8")

    assert "Market Research Strategy Benchmark Report" in report
    assert "successful_baseline" in report
    assert "accept_everything" in report
    assert "Success rate" in report
    assert "Accepts stale or unsupported evidence" in report
