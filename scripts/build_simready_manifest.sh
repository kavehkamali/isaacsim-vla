#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"
REPO_DIR="$ROOT_DIR"
RESULTS_DIR="$ROOT_DIR/results"
ASSETS_DIR="$ROOT_DIR/third_party/assets"

mkdir -p "$RESULTS_DIR"

python3 "$REPO_DIR/tools/build_asset_manifest.py" \
  --root "$ASSETS_DIR/scene_templates" \
  --root "$ASSETS_DIR/simready_furniture" \
  --root "$ASSETS_DIR/base_materials" \
  --output "$RESULTS_DIR/simready_manifest.json"
