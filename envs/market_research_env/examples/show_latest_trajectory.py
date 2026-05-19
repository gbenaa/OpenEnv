"""Show a concise summary of the latest market-research trajectory.

The environment writes JSONL trajectory files when an episode finishes.
By default those files are stored in:

    /tmp/market_research_env/trajectories/

Use this helper after running scripts/run_baseline_episode.sh.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_TRAJECTORY_DIR = Path("/tmp/market_research_env/trajectories")


def load_events(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                events.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number} of {path}") from exc
    return events


def latest_trajectory(trajectory_dir: Path) -> Path:
    files = sorted(
        trajectory_dir.glob("*.jsonl"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not files:
        raise FileNotFoundError(f"No trajectory JSONL files found in {trajectory_dir}")
    return files[0]


def action_type(event: dict[str, Any]) -> str:
    payload = event.get("payload", {})
    action = payload.get("action", {})
    if isinstance(action, dict):
        return str(action.get("action_type", ""))
    return ""


def summarise(events: list[dict[str, Any]]) -> dict[str, Any]:
    step_events = [event for event in events if event.get("event_type") == "step"]
    action_counts: dict[str, int] = {}
    total_reward = 0.0
    final_score_details: dict[str, Any] = {}
    errors: list[str] = []

    for event in step_events:
        payload = event.get("payload", {})
        action = action_type(event) or "<unknown>"
        action_counts[action] = action_counts.get(action, 0) + 1

        reward = payload.get("reward", 0.0)
        if isinstance(reward, (int, float)):
            total_reward += float(reward)

        error = payload.get("error")
        if error:
            errors.append(str(error))

        score_details = payload.get("score_details")
        if isinstance(score_details, dict) and score_details.get("event") == "submit":
            final_score_details = score_details

    return {
        "events": len(events),
        "steps": len(step_events),
        "action_counts": action_counts,
        "total_reward_from_steps": total_reward,
        "final_score_details": final_score_details,
        "errors": errors,
    }


def print_summary(path: Path, summary: dict[str, Any]) -> None:
    print(f"trajectory={path}")
    print(f"events={summary['events']}")
    print(f"steps={summary['steps']}")
    print(f"total_reward_from_steps={summary['total_reward_from_steps']}")

    final_score_details = summary.get("final_score_details") or {}
    if final_score_details:
        print(f"success={final_score_details.get('success')}")
        print(f"final_reasons={final_score_details.get('reasons')}")

    print("actions:")
    for action, count in sorted(summary["action_counts"].items()):
        print(f"  {action}: {count}")

    errors = summary.get("errors") or []
    if errors:
        print("errors:")
        for error in errors:
            print(f"  {error}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Show the latest market-research trajectory summary."
    )
    parser.add_argument(
        "--trajectory-dir",
        default=str(DEFAULT_TRAJECTORY_DIR),
        help="Directory containing trajectory JSONL files.",
    )
    parser.add_argument(
        "--file",
        default=None,
        help="Specific trajectory JSONL file to inspect.",
    )
    args = parser.parse_args()

    if args.file:
        path = Path(args.file).expanduser().resolve()
    else:
        path = latest_trajectory(Path(args.trajectory_dir).expanduser().resolve())

    events = load_events(path)
    print_summary(path, summarise(events))


if __name__ == "__main__":
    main()
