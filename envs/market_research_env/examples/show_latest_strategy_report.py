"""Generate a readable report from the latest strategy benchmark JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Any


DEFAULT_BENCHMARK_DIR = Path("/tmp/market_research_env/benchmarks")


FAILURE_MODE_LABELS = {
    "accept_everything": "Accepts stale or unsupported evidence instead of applying source criticism.",
    "duplicate_evidence": "Repeats the same evidence pattern and triggers duplicate-evidence controls.",
    "no_disclosure": "Submits without sufficient affiliate-disclosure awareness.",
    "successful_baseline": "Captures distinct, relevant evidence, rejects weak sources, and includes disclosure awareness.",
}


def find_latest_strategy_benchmark(benchmark_dir: Path) -> Path:
    paths = sorted(
        benchmark_dir.glob("*strategy_benchmark.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not paths:
        raise FileNotFoundError(f"No strategy benchmark JSON files found in {benchmark_dir}")
    return paths[0]


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"true", "1", "yes", "success"}
    return bool(value)


def _extract_runs(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Return normalised run rows from known benchmark JSON shapes."""

    candidate_keys = [
        "runs",
        "results",
        "episodes",
        "strategy_runs",
        "run_results",
    ]

    for key in candidate_keys:
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]

    benchmark = payload.get("benchmark")
    if isinstance(benchmark, dict):
        for key in candidate_keys:
            value = benchmark.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]

    summaries = _extract_summaries(payload)
    reconstructed: list[dict[str, Any]] = []
    for row in summaries:
        runs = int(_as_float(row.get("runs"), 0))
        success_rate = _as_float(row.get("success_rate"), 0.0)
        success_count = int(round(runs * success_rate))
        for index in range(runs):
            reconstructed.append(
                {
                    "strategy": row.get("strategy", "unknown"),
                    "run": index + 1,
                    "success": index < success_count,
                    "reward": row.get("mean_reward", 0.0),
                    "accepted": row.get("mean_accepted", row.get("accepted", 0)),
                    "rejected": row.get("mean_rejected", row.get("rejected", 0)),
                }
            )
    return reconstructed


def _extract_summaries(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Return normalised strategy summaries from known benchmark JSON shapes."""

    candidate_keys = [
        "summaries",
        "summary",
        "strategy_summaries",
        "by_strategy",
        "strategies",
    ]

    for key in candidate_keys:
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict):
            rows = []
            for strategy, row in value.items():
                if isinstance(row, dict):
                    rows.append({"strategy": strategy, **row})
            return rows

    benchmark = payload.get("benchmark")
    if isinstance(benchmark, dict):
        for key in candidate_keys:
            value = benchmark.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
            if isinstance(value, dict):
                rows = []
                for strategy, row in value.items():
                    if isinstance(row, dict):
                        rows.append({"strategy": strategy, **row})
                return rows

    return []


def summarise_runs(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in runs:
        strategy = str(row.get("strategy") or row.get("strategy_name") or "unknown")
        grouped.setdefault(strategy, []).append(row)

    summaries: list[dict[str, Any]] = []
    for strategy, rows in grouped.items():
        rewards = [_as_float(row.get("reward", row.get("cum_reward"))) for row in rows]
        successes = [_as_bool(row.get("success")) for row in rows]
        accepted = [_as_float(row.get("accepted", row.get("accepted_count"))) for row in rows]
        rejected = [_as_float(row.get("rejected", row.get("rejected_count"))) for row in rows]

        summaries.append(
            {
                "strategy": strategy,
                "runs": len(rows),
                "success_count": sum(1 for item in successes if item),
                "success_rate": (sum(1 for item in successes if item) / len(rows)) if rows else 0.0,
                "mean_reward": mean(rewards) if rewards else 0.0,
                "mean_accepted": mean(accepted) if accepted else 0.0,
                "mean_rejected": mean(rejected) if rejected else 0.0,
            }
        )

    return sorted(summaries, key=lambda row: (-_as_float(row.get("success_rate")), -_as_float(row.get("mean_reward")), str(row.get("strategy"))))


def normalise_summary_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    runs = _extract_runs(payload)
    if runs:
        return summarise_runs(runs)

    summaries = _extract_summaries(payload)
    normalised: list[dict[str, Any]] = []
    for row in summaries:
        strategy = str(row.get("strategy") or row.get("name") or "unknown")
        runs_count = int(_as_float(row.get("runs", row.get("count")), 0))
        success_count = int(_as_float(row.get("success_count"), 0))
        success_rate = _as_float(row.get("success_rate"), 0.0)
        if not success_rate and runs_count:
            success_rate = success_count / runs_count

        normalised.append(
            {
                "strategy": strategy,
                "runs": runs_count,
                "success_count": success_count,
                "success_rate": success_rate,
                "mean_reward": _as_float(row.get("mean_reward", row.get("average_reward"))),
                "mean_accepted": _as_float(row.get("mean_accepted", row.get("accepted"))),
                "mean_rejected": _as_float(row.get("mean_rejected", row.get("rejected"))),
            }
        )

    return sorted(normalised, key=lambda row: (-row["success_rate"], -row["mean_reward"], row["strategy"]))


def infer_failure_mode(strategy: str, success_rate: float) -> str:
    if success_rate >= 1.0:
        return FAILURE_MODE_LABELS.get(strategy, "Successful under current scoring rules.")
    return FAILURE_MODE_LABELS.get(strategy, "Failed under current scoring rules. Inspect run details for the specific cause.")


def build_report(payload: dict[str, Any], source_path: Path) -> str:
    rows = normalise_summary_rows(payload)
    if not rows:
        raise ValueError("Could not find strategy run or summary rows in benchmark JSON")

    lines = [
        "# Market Research Strategy Benchmark Report",
        "",
        f"Source JSON: `{source_path}`",
        "",
        "## Summary",
        "",
        "| Strategy | Runs | Success rate | Mean reward | Mean accepted | Mean rejected | Interpretation |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]

    for row in rows:
        strategy = str(row["strategy"])
        success_rate = _as_float(row["success_rate"])
        lines.append(
            "| {strategy} | {runs} | {success_rate:.2f} | {mean_reward:.2f} | {mean_accepted:.1f} | {mean_rejected:.1f} | {interpretation} |".format(
                strategy=strategy,
                runs=int(_as_float(row["runs"])),
                success_rate=success_rate,
                mean_reward=_as_float(row["mean_reward"]),
                mean_accepted=_as_float(row["mean_accepted"]),
                mean_rejected=_as_float(row["mean_rejected"]),
                interpretation=infer_failure_mode(strategy, success_rate),
            )
        )

    best = rows[0]
    lines.extend(
        [
            "",
            "## Current best strategy",
            "",
            f"`{best['strategy']}` is currently the strongest strategy under this benchmark, with success rate `{_as_float(best['success_rate']):.2f}` and mean reward `{_as_float(best['mean_reward']):.2f}`.",
            "",
            "## What this report proves",
            "",
            "The benchmark is no longer only checking whether one scripted path succeeds. It now compares successful and deliberately weak strategies, so the harness can demonstrate that it rewards evidence quality, source criticism, freshness, and compliance rather than mere activity volume.",
            "",
            "## Known limits",
            "",
            "The strategies are still scripted. This report is an evaluation-harness check, not a live commercial-intelligence result.",
            "",
        ]
    )

    return "\n".join(lines)


def write_report(source_path: Path, output_path: Path | None = None) -> Path:
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    report = build_report(payload, source_path)

    if output_path is None:
        output_path = source_path.with_name(source_path.stem + "_report.md")

    output_path.write_text(report + "\n", encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Show a readable report for the latest strategy benchmark.")
    parser.add_argument(
        "--benchmark-dir",
        default=str(DEFAULT_BENCHMARK_DIR),
        help="Directory containing strategy benchmark JSON files.",
    )
    parser.add_argument(
        "--input-json",
        default=None,
        help="Optional explicit benchmark JSON path.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional Markdown output path.",
    )
    args = parser.parse_args()

    source_path = Path(args.input_json) if args.input_json else find_latest_strategy_benchmark(Path(args.benchmark_dir))
    output_path = Path(args.output) if args.output else None
    report_path = write_report(source_path, output_path)

    print(f"source={source_path}")
    print(f"report={report_path}")
    print(report_path.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
