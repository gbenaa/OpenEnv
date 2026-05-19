#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python examples/show_latest_human_review_report.py "$@"
