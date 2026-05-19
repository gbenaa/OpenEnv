#!/usr/bin/env bash
set -euo pipefail

export ENABLE_WEB_INTERFACE="${ENABLE_WEB_INTERFACE:-true}"
export MARKET_RESEARCH_PORT="${MARKET_RESEARCH_PORT:-8000}"

python -m market_research_env.server.app
