#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRACK_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HUB_ROOT="$(cd "$TRACK_ROOT/.." && pwd)"

source "$HUB_ROOT/scripts/env.sh"

cd "$TRACK_ROOT"
PYTHON_BIN="${PYTHON:-../.venv/bin/python}"
CONFIG="${1:-scripts/train_config.yaml}"
if [[ $# -gt 0 ]]; then
  shift
fi
exec "$PYTHON_BIN" scripts/train.py --config "$CONFIG" "$@"
