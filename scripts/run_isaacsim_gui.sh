#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"
ISAACSIM_DIR="$ROOT_DIR/third_party/isaacsim"
REPO_DIR="$ROOT_DIR"
STAGE_USD="${2:-}"

export CUDA_VISIBLE_DEVICES=0

if [[ -z "$STAGE_USD" ]]; then
  eval "$("$REPO_DIR/scripts/prepare_lightwheel_kitchen.sh" "$ROOT_DIR")"
  STAGE_USD="${LIGHTWHEEL_STAGE_USD}"
fi

if [[ ! -x "$ISAACSIM_DIR/python.sh" ]]; then
  echo "Missing Isaac Sim runtime at $ISAACSIM_DIR" >&2
  echo "Run ./scripts/prepare_workspace.sh first." >&2
  exit 2
fi

cd "$ISAACSIM_DIR"
./python.sh "$REPO_DIR/scripts/gui_open_stage.py" --stage-usd "$STAGE_USD"
