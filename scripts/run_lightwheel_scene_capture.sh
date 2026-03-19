#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"
ISAACSIM_DIR="$ROOT_DIR/third_party/isaacsim"
REPO_DIR="$ROOT_DIR"
DEFAULT_STAGE_USD="$ROOT_DIR/third_party/Lightwheel_Kitchen/Collected_KitchenRoom/KitchenRoom.usd"
STAGE_USD="${2:-}"
OUTPUT_DIR="${3:-$ROOT_DIR/results/lightwheel_scene}"
FRAMES_DIR="$OUTPUT_DIR/frames"
VIDEO_PATH="$OUTPUT_DIR/lightwheel_kitchen_scene.mp4"

export CUDA_VISIBLE_DEVICES=0

if [[ -z "$STAGE_USD" ]]; then
  eval "$("$REPO_DIR/scripts/prepare_lightwheel_kitchen.sh" "$ROOT_DIR")"
  STAGE_USD="${STAGE_USD:-${LIGHTWHEEL_STAGE_USD:-$DEFAULT_STAGE_USD}}"
fi

mkdir -p "$FRAMES_DIR"
cd "$ISAACSIM_DIR"

./python.sh "$REPO_DIR/scripts/headless_lightwheel_scene_record.py" \
  --stage-usd "$STAGE_USD" \
  --frames-dir "$FRAMES_DIR" \
  --max-frames 120 \
  --width 1280 \
  --height 720

if ! ls "$FRAMES_DIR"/frame_*.png >/dev/null 2>&1; then
  echo "no_frames_written"
  exit 2
fi

ffmpeg -y -framerate 24 -i "$FRAMES_DIR/frame_%05d.png" -c:v libx264 -pix_fmt yuv420p "$VIDEO_PATH"
echo "$VIDEO_PATH"
