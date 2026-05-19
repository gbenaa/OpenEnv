#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python examples/run_strategy_benchmark.py "$@"
