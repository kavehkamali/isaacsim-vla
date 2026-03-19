#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"
ISAACSIM_DIR="$ROOT_DIR/third_party/isaacsim"
REPO_DIR="$ROOT_DIR"
DEFAULT_STAGE_USD="$ROOT_DIR/third_party/Lightwheel_Kitchen/Collected_KitchenRoom/KitchenRoom.usd"
DEFAULT_PROP_USD="$ROOT_DIR/third_party/Lightwheel_Kitchen/Collected_KitchenRoom/Kitchen_Other/Kitchen_Bottle.usd"
STAGE_USD="${2:-}"
PROP_USD="${3:-}"
OUTPUT_DIR="${4:-$ROOT_DIR/results/lightwheel_pick_place}"
VIDEO_PATH="$OUTPUT_DIR/lightwheel_pick_place.mp4"
KEEP_FRAMES="${KEEP_FRAMES:-0}"
KIT_ARGS=(
  "--/rtx/verifyDriverVersion/enabled=false"
)

export CUDA_VISIBLE_DEVICES=0

if [[ -z "$STAGE_USD" || -z "$PROP_USD" ]]; then
  eval "$("$REPO_DIR/scripts/prepare_lightwheel_kitchen.sh" "$ROOT_DIR")"
  STAGE_USD="${STAGE_USD:-${LIGHTWHEEL_STAGE_USD:-$DEFAULT_STAGE_USD}}"
  PROP_USD="${PROP_USD:-${LIGHTWHEEL_PROP_USD:-$DEFAULT_PROP_USD}}"
fi

mkdir -p "$OUTPUT_DIR"
cd "$ISAACSIM_DIR"

RUN_ARGS=(
  "$REPO_DIR/scripts/headless_lightwheel_pick_place_record.py"
  "${KIT_ARGS[@]}"
  --stage-usd "$STAGE_USD"
  --prop-usd "$PROP_USD"
  --video-path "$VIDEO_PATH"
  --max-steps 360
  --frame-stride 2
  --width 1280
  --height 720
)

if [[ "$KEEP_FRAMES" == "1" ]]; then
  FRAMES_DIR="$OUTPUT_DIR/frames"
  mkdir -p "$FRAMES_DIR"
  RUN_ARGS+=(--frames-dir "$FRAMES_DIR")
fi

./python.sh "${RUN_ARGS[@]}"

if [[ ! -f "$VIDEO_PATH" ]]; then
  echo "video_not_written"
  exit 2
fi

echo "$VIDEO_PATH"
