#!/bin/zsh
set -euo pipefail

readonly DEFAULT_PORT=8769
readonly SCRIPT_DIR="${0:A:h}"
readonly PROJECT_ROOT="${SCRIPT_DIR:h}"

if (( $# > 1 )); then
  print -u2 -- "Usage: ${0:t} [port]"
  exit 64
fi

if (( $# == 1 )); then
  readonly PORT="$1"
else
  readonly PORT="$DEFAULT_PORT"
fi

if [[ "$PORT" != <1024-65535> ]]; then
  print -u2 -- "Port must be a numeric value from 1024 to 65535."
  exit 64
fi

cd "$PROJECT_ROOT"
print -- "Starting W09 research workbench at http://127.0.0.1:${PORT}/"
print -- "Press Control-C in this terminal to stop the workbench."
exec uv run --locked uvicorn services.api.w09_main:app \
  --host 127.0.0.1 \
  --port "$PORT" \
  --no-access-log
