"""Show a recommendation-facing summary from the latest exported bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from market_research_env.server.recommendation_model import (
    build_recommendation_summary,
    summary_to_markdown,
)


def find_latest_bundle(bundle_dir: Path) -> Path:
    paths = sorted(bundle_dir.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not paths:
        raise FileNotFoundError(f"No JSON bundle exports found in {bundle_dir}")
    return paths[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Show latest recommendation evidence summary.")
    parser.add_argument(
        "--bundle-dir",
        default="/tmp/market_research_env/bundles",
        help="Directory containing exported evidence bundle JSON files.",
    )
    args = parser.parse_args()

    bundle_path = find_latest_bundle(Path(args.bundle_dir))
    payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    summary = build_recommendation_summary(payload)

    print(f"bundle={bundle_path}")
    print(f"task_id={summary.task_id}")
    print(f"product_signals={len(summary.product_signals)}")
    print(f"source_count={summary.source_count}")
    print()
    print(summary_to_markdown(summary))


if __name__ == "__main__":
    main()
