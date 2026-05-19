#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python examples/run_in_process_baseline_episode.py
