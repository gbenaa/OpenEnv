from market_research_env.examples.run_cross_task_benchmark import (
    parse_bool,
    parse_key_value_output,
    summarise,
)


def test_parse_key_value_output():
    parsed = parse_key_value_output(
        "done=True\nsuccess=True\naccepted=6\nrejected=2\ncum_reward=67.5\n"
    )

    assert parsed["success"] == "True"
    assert parsed["accepted"] == "6"
    assert parsed["cum_reward"] == "67.5"


def test_parse_bool():
    assert parse_bool("True") is True
    assert parse_bool("true") is True
    assert parse_bool("False") is False
    assert parse_bool(None) is False


def test_cross_task_summary_distinguishes_conclusions():
    rows = [
        {
            "label": "positive_baseline",
            "task_id": "uk_espresso_001",
            "success": True,
            "reward": 67.5,
            "accepted": 6,
            "rejected": 2,
            "expected_conclusion": "sufficient_evidence",
            "observed_conclusion": "sufficient_evidence",
        },
        {
            "label": "negative_control",
            "task_id": "uk_smart_rings_negative_001",
            "success": True,
            "reward": 42.0,
            "accepted": 1,
            "rejected": 4,
            "expected_conclusion": "insufficient_evidence",
            "observed_conclusion": "insufficient_evidence",
        },
    ]

    summary = summarise(rows)
    by_label = {item["label"]: item for item in summary}

    assert by_label["positive_baseline"]["expected_conclusion"] == "sufficient_evidence"
    assert by_label["negative_control"]["expected_conclusion"] == "insufficient_evidence"
    assert by_label["negative_control"]["conclusion_match_count"] == 1
