"""Show the latest exported market-research evidence bundle."""

from __future__ import annotations

from pathlib import Path
import json
import os
import sys


def find_latest_bundle(output_dir: Path) -> Path:
    bundle_dir = output_dir / "bundles"
    if not bundle_dir.exists():
        raise SystemExit(f"No bundle directory found: {bundle_dir}")

    bundle_paths = sorted(bundle_dir.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not bundle_paths:
        raise SystemExit(f"No JSON bundle exports found in: {bundle_dir}")

    return bundle_paths[0]


def main() -> int:
    output_dir = Path(os.environ.get("MARKET_RESEARCH_OUTPUT_DIR", "/tmp/market_research_env"))
    path = find_latest_bundle(output_dir)

    payload = json.loads(path.read_text(encoding="utf-8"))
    bundle = payload.get("bundle", {})
    score_details = payload.get("score_details", {})

    print(f"json={path}")
    markdown_path = path.with_suffix(".md")
    if markdown_path.exists():
        print(f"markdown={markdown_path}")

    print(f"episode_id={payload.get('episode_id', '')}")
    print(f"task_id={bundle.get('task_id', '')}")
    print(f"submitted={bundle.get('submitted', False)}")
    print(f"success={score_details.get('success', False)}")
    print(f"cum_reward={bundle.get('cum_reward', 0.0)}")
    print(f"accepted={len(bundle.get('accepted_evidence', []))}")
    print(f"rejected={len(bundle.get('rejected_evidence', []))}")
    print(f"pending={len(bundle.get('pending_evidence', []))}")

    reasons = score_details.get("reasons", [])
    if reasons:
        print("reasons=" + ", ".join(reasons))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
