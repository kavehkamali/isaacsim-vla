#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"
ISAACSIM_DIR="$ROOT_DIR/third_party/isaacsim"
REPO_DIR="$ROOT_DIR"
KIT_ARGS=(
  "--/rtx/verifyDriverVersion/enabled=false"
)

if [[ ! -x "$ISAACSIM_DIR/python.sh" ]]; then
  echo "Missing Isaac Sim runtime at $ISAACSIM_DIR" >&2
  echo "Run ./scripts/prepare_workspace.sh first." >&2
  exit 2
fi

eval "$("$REPO_DIR/scripts/prepare_lightwheel_kitchen.sh" "$ROOT_DIR")"
STAGE_USD="${LIGHTWHEEL_STAGE_USD}"
PROP_USD="${LIGHTWHEEL_PROP_USD}"

export CUDA_VISIBLE_DEVICES=0

cd "$ISAACSIM_DIR"
./python.sh "$REPO_DIR/scripts/gui_open_stage.py" \
  "${KIT_ARGS[@]}" \
  --stage-usd "$STAGE_USD" \
  --prop-usd "$PROP_USD" \
  --spawn-benchmark-pick-setup
