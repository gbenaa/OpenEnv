"""Generate and print a human-review report for the latest exported bundle."""

from __future__ import annotations

import argparse

from market_research_env.server.human_review_report import (
    find_latest_bundle_json,
    write_human_review_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Show the latest market-research human-review report.")
    parser.add_argument(
        "--bundle-dir",
        default="/tmp/market_research_env/bundles",
        help="Directory containing exported bundle JSON files.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Optional directory for human-review Markdown reports.",
    )
    args = parser.parse_args()

    bundle_path = find_latest_bundle_json(args.bundle_dir)
    report_path = write_human_review_report(bundle_path, output_dir=args.output_dir)

    print(f"bundle={bundle_path}")
    print(f"report={report_path}")
    print(report_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
