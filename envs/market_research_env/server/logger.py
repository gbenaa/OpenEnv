"""Trajectory logger for market-research episodes."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


class TrajectoryLogger:
    """Append JSONL events for an episode."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.events: list[dict[str, Any]] = []

    def reset(self) -> None:
        self.events = []

    def log(self, event_type: str, payload: dict[str, Any]) -> None:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "event_type": event_type,
            "payload": payload,
        }
        self.events.append(event)

    def write(self, episode_id: str) -> Path:
        path = self.output_dir / f"{episode_id}.jsonl"
        with path.open("w", encoding="utf-8") as handle:
            for event in self.events:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        return path
