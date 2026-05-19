"""Run a small cross-task benchmark for market_research_env.

The purpose is to show that the environment can report both a positive task
where evidence is sufficient and a negative-control task where the correct
conclusion is insufficient evidence.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path("/tmp/market_research_env/cross_task_benchmarks")


TASKS = [
    {
        "task_id": "uk_espresso_001",
        "label": "positive_baseline",
        "expected_conclusion": "sufficient_evidence",
        "script": ROOT / "examples" / "run_in_process_baseline_episode.py",
    },
    {
        "task_id": "uk_smart_rings_negative_001",
        "label": "negative_control",
        "expected_conclusion": "insufficient_evidence",
        "script": ROOT / "examples" / "run_negative_control_baseline.py",
    },
]


def parse_key_value_output(output: str) -> dict[str, str]:
    """Parse simple key=value lines from a baseline script."""
    result: dict[str, str] = {}
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key:
            result[key] = value
    return result


def parse_bool(value: str | None) -> bool:
    return str(value).strip().lower() == "true"


def parse_float(value: str | None) -> float:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return 0.0


def parse_int(value: str | None) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return 0


def run_task(task: dict[str, Any], run_index: int) -> dict[str, Any]:
    """Run one task baseline and return normalised benchmark data."""
    proc = subprocess.run(
        [sys.executable, str(task["script"])],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    parsed = parse_key_value_output(proc.stdout)
    success = parse_bool(parsed.get("success")) and proc.returncode == 0
    observed_conclusion = parsed.get("expected_conclusion", task["expected_conclusion"])

    row = {
        "task_id": task["task_id"],
        "label": task["label"],
        "run": run_index,
        "returncode": proc.returncode,
        "success": success,
        "expected_conclusion": task["expected_conclusion"],
        "observed_conclusion": observed_conclusion,
        "reward": parse_float(parsed.get("cum_reward")),
        "accepted": parse_int(parsed.get("accepted")),
        "rejected": parse_int(parsed.get("rejected")),
        "stdout": proc.stdout,
        "stderr_tail": proc.stderr.splitlines()[-10:],
    }
    return row


def summarise(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Summarise rows by task label."""
    labels = sorted({row["label"] for row in rows})
    summary: list[dict[str, Any]] = []

    for label in labels:
        group = [row for row in rows if row["label"] == label]
        rewards = [float(row["reward"]) for row in group]
        success_count = sum(1 for row in group if row["success"])
        conclusion_match_count = sum(
            1
            for row in group
            if row["observed_conclusion"] == row["expected_conclusion"]
        )
        summary.append(
            {
                "label": label,
                "task_id": group[0]["task_id"],
                "runs": len(group),
                "success_count": success_count,
                "success_rate": success_count / len(group) if group else 0.0,
                "mean_reward": mean(rewards) if rewards else 0.0,
                "mean_accepted": mean([row["accepted"] for row in group]) if group else 0.0,
                "mean_rejected": mean([row["rejected"] for row in group]) if group else 0.0,
                "expected_conclusion": group[0]["expected_conclusion"],
                "conclusion_match_count": conclusion_match_count,
            }
        )

    return summary


def write_outputs(rows: list[dict[str, Any]], summary: list[dict[str, Any]]) -> dict[str, str]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    json_path = OUTPUT_DIR / f"{stamp}_cross_task_benchmark.json"
    markdown_path = OUTPUT_DIR / f"{stamp}_cross_task_benchmark.md"

    payload = {
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "rows": rows,
        "summary": summary,
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Cross-Task Market Research Benchmark",
        "",
        "## Summary",
        "",
        "| Label | Task | Runs | Success rate | Mean reward | Mean accepted | Mean rejected | Expected conclusion |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for item in summary:
        lines.append(
            "| {label} | {task_id} | {runs} | {success_rate:.2f} | {mean_reward:.2f} | {mean_accepted:.1f} | {mean_rejected:.1f} | {expected_conclusion} |".format(
                **item
            )
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The positive baseline should succeed by accepting enough distinct, current, useful evidence for a buying-guide decision.",
            "",
            "The negative-control baseline should also succeed, but for the opposite reason: it should reject weak, stale, or unsupported sources and conclude that evidence is insufficient.",
            "",
            "This report checks that the harness can represent both sufficiency and insufficiency cases across tasks.",
        ]
    )
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {"json": str(json_path), "markdown": str(markdown_path)}


def run_benchmark(runs: int) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for run_index in range(1, runs + 1):
        for task in TASKS:
            row = run_task(task, run_index)
            rows.append(row)
            print(
                "task={task_id} label={label} run={run} success={success} reward={reward} accepted={accepted} rejected={rejected} conclusion={observed_conclusion}".format(
                    **row
                )
            )

    summary = summarise(rows)
    paths = write_outputs(rows, summary)

    print(f"tasks={len(TASKS)}")
    print(f"runs_per_task={runs}")
    for item in summary:
        print(
            "label={label} success_rate={success_rate:.2f} mean_reward={mean_reward:.2f} expected_conclusion={expected_conclusion}".format(
                **item
            )
        )
    print(f"json={paths['json']}")
    print(f"markdown={paths['markdown']}")

    return {"rows": rows, "summary": summary, "paths": paths}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=1)
    args = parser.parse_args()

    if args.runs < 1:
        raise SystemExit("--runs must be at least 1")

    result = run_benchmark(args.runs)
    if not all(row["success"] for row in result["rows"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
