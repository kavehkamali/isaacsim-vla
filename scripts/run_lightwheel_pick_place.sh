#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:-/home/kaveh/project/isaacsim_vla_muglift_lab_2026-03-18}"
ISAACSIM_DIR="$ROOT_DIR/isaacsim"
REPO_DIR="$ROOT_DIR/repo/isaacsim-vla"
STAGE_USD="${2:-$ROOT_DIR/assets/lightwheel_kitchen/Collected_KitchenRoom/KitchenRoom.usd}"
PROP_USD="${3:-$ROOT_DIR/assets/lightwheel_kitchen/Collected_KitchenRoom/Kitchen_Other/Kitchen_Bottle.usd}"
OUTPUT_DIR="${4:-$ROOT_DIR/results/lightwheel_pick_place}"
FRAMES_DIR="$OUTPUT_DIR/frames"
VIDEO_PATH="$OUTPUT_DIR/lightwheel_pick_place.mp4"

export CUDA_VISIBLE_DEVICES=0

mkdir -p "$FRAMES_DIR"
cd "$ISAACSIM_DIR"

./python.sh "$REPO_DIR/scripts/headless_lightwheel_pick_place_record.py" \
  --stage-usd "$STAGE_USD" \
  --prop-usd "$PROP_USD" \
  --frames-dir "$FRAMES_DIR" \
  --max-steps 720 \
  --frame-stride 2 \
  --width 1280 \
  --height 720

if ! ls "$FRAMES_DIR"/frame_*.png >/dev/null 2>&1; then
  echo "no_frames_written"
  exit 2
fi

ffmpeg -y -framerate 15 -i "$FRAMES_DIR/frame_%05d.png" -c:v libx264 -pix_fmt yuv420p "$VIDEO_PATH"
echo "$VIDEO_PATH"
