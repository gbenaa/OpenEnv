#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python examples/run_benchmark.py "$@"
