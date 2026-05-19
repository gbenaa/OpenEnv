from pathlib import Path
import importlib.util


def load_benchmark_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "examples" / "run_benchmark.py"
    spec = importlib.util.spec_from_file_location("run_benchmark", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_build_summary_counts_success_and_reward():
    module = load_benchmark_module()

    summary = module.build_summary(
        [
            {"success": True, "cum_reward": 67.5},
            {"success": False, "cum_reward": 10.0},
        ]
    )

    assert summary["runs"] == 2
    assert summary["success_count"] == 1
    assert summary["success_rate"] == 0.5
    assert summary["mean_reward"] == 38.75
    assert summary["min_reward"] == 10.0
    assert summary["max_reward"] == 67.5


def test_write_summary_outputs_json_and_markdown(tmp_path):
    module = load_benchmark_module()

    summary = module.build_summary(
        [
            {
                "success": True,
                "cum_reward": 67.5,
                "accepted_count": 6,
                "rejected_count": 2,
                "pending_count": 0,
                "episode_id": "episode_test",
            }
        ]
    )

    paths = module.write_summary(summary, tmp_path)

    assert Path(paths["json"]).exists()
    assert Path(paths["markdown"]).exists()
    assert "Success rate" in Path(paths["markdown"]).read_text(encoding="utf-8")
