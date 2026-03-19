#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"
DOWNLOADS_DIR="$ROOT_DIR/third_party/downloads"
ASSETS_DIR="$ROOT_DIR/third_party/assets"
SCENE_TEMPLATES_ZIP="$DOWNLOADS_DIR/Scene_Templates_NVD@10011.zip"
SIMREADY_FURNITURE_ZIP="$DOWNLOADS_DIR/SimReady_Furniture_Misc_01_NVD@10010.zip"
BASE_MATERIALS_ZIP="$DOWNLOADS_DIR/Base_Materials_NVD@10013.zip"

mkdir -p "$ASSETS_DIR/scene_templates"
mkdir -p "$ASSETS_DIR/simready_furniture"
mkdir -p "$ASSETS_DIR/base_materials"

if [[ ! -f "$SCENE_TEMPLATES_ZIP" ]]; then
  echo "Missing scene templates archive: $SCENE_TEMPLATES_ZIP" >&2
  exit 2
fi

if [[ ! -f "$SIMREADY_FURNITURE_ZIP" ]]; then
  echo "Missing SimReady furniture archive: $SIMREADY_FURNITURE_ZIP" >&2
  exit 2
fi

unzip -n "$SCENE_TEMPLATES_ZIP" -d "$ASSETS_DIR/scene_templates"
unzip -n "$SIMREADY_FURNITURE_ZIP" -d "$ASSETS_DIR/simready_furniture"

if [[ -f "$BASE_MATERIALS_ZIP" ]]; then
  unzip -n "$BASE_MATERIALS_ZIP" -d "$ASSETS_DIR/base_materials"
else
  echo "Base materials pack not present; continuing without it."
fi
