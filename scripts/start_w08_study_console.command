#!/bin/zsh
set -euo pipefail

CONSOLE_SCRIPT_DIR="${0:A:h}"
cd "$CONSOLE_SCRIPT_DIR/.."
exec uv run python scripts/run_w08_study.py console
