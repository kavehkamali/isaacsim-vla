#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:-/home/kaveh/project/isaacsim_vla_muglift_lab_2026-03-18}"
ISAACSIM_DIR="$ROOT_DIR/isaacsim"
REPO_DIR="$ROOT_DIR/repo/isaacsim-vla"
OUTPUT_DIR="${2:-$ROOT_DIR/results/smoke_pick_place}"
FRAMES_DIR="$OUTPUT_DIR/frames"
VIDEO_PATH="$OUTPUT_DIR/smoke_pick_place.mp4"

export CUDA_VISIBLE_DEVICES=0

mkdir -p "$FRAMES_DIR"
cd "$ISAACSIM_DIR"

./python.sh "$REPO_DIR/scripts/headless_pick_place_record.py" \
  --frames-dir "$FRAMES_DIR" \
  --max-steps 720 \
  --frame-stride 2

ffmpeg -y -framerate 15 -i "$FRAMES_DIR/frame_%05d.png" -c:v libx264 -pix_fmt yuv420p "$VIDEO_PATH"
echo "$VIDEO_PATH"
