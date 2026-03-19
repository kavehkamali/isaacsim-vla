#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"
ISAACSIM_DIR="$ROOT_DIR/third_party/isaacsim"
ASSETS_ROOT_OVERRIDE="${2:-}"

export CUDA_VISIBLE_DEVICES=0

EXTRA_ARGS=(
  "--reset-user"
  "--/renderer/activeGpu=0"
  "--/renderer/multiGpu/enabled=false"
  "--/rtx/verifyDriverVersion/enabled=false"
)

if [[ -n "$ASSETS_ROOT_OVERRIDE" ]]; then
  EXTRA_ARGS+=("--/persistent/isaac/asset_root/default=$ASSETS_ROOT_OVERRIDE")
fi

cd "$ISAACSIM_DIR"
./python.sh standalone_examples/api/isaacsim.robot.manipulators/franka/pick_place.py "${EXTRA_ARGS[@]}"
