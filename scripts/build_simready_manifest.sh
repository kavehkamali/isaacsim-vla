#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:-/home/kaveh/project/isaacsim_vla_muglift_lab_2026-03-18}"
REPO_DIR="$ROOT_DIR/repo/isaacsim-vla"
RESULTS_DIR="$ROOT_DIR/results"
ASSETS_DIR="$ROOT_DIR/assets"

mkdir -p "$RESULTS_DIR"

python3 "$REPO_DIR/tools/build_asset_manifest.py" \
  --root "$ASSETS_DIR/scene_templates" \
  --root "$ASSETS_DIR/simready_furniture" \
  --root "$ASSETS_DIR/base_materials" \
  --output "$RESULTS_DIR/simready_manifest.json"
