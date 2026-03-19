#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:-/home/kaveh/project/isaacsim_vla_muglift_lab_2026-03-18}"
ISAACSIM_DIR="$ROOT_DIR/isaacsim"
ASSETS_ROOT_OVERRIDE="${2:-}"

export CUDA_VISIBLE_DEVICES=0

EXTRA_ARGS=(
  "--reset-user"
  "--/renderer/activeGpu=0"
  "--/renderer/multiGpu/enabled=false"
)

if [[ -n "$ASSETS_ROOT_OVERRIDE" ]]; then
  EXTRA_ARGS+=("--/persistent/isaac/asset_root/default=$ASSETS_ROOT_OVERRIDE")
fi

cd "$ISAACSIM_DIR"
./python.sh standalone_examples/api/isaacsim.robot.manipulators/franka/pick_place.py "${EXTRA_ARGS[@]}"
