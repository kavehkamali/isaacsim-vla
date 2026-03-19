#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:-/home/kaveh/project/isaacsim_vla_muglift_lab_2026-03-18}"
DOWNLOADS_DIR="$ROOT_DIR/downloads"
ASSETS_DIR="$ROOT_DIR/assets"

mkdir -p "$ASSETS_DIR/scene_templates"
mkdir -p "$ASSETS_DIR/simready_furniture"
mkdir -p "$ASSETS_DIR/base_materials"

unzip -n "$DOWNLOADS_DIR/Scene_Templates_NVD@10011.zip" -d "$ASSETS_DIR/scene_templates"
unzip -n "$DOWNLOADS_DIR/SimReady_Furniture_Misc_01_NVD@10010.zip" -d "$ASSETS_DIR/simready_furniture"

if [[ -f "$DOWNLOADS_DIR/Base_Materials_NVD@10013.zip" ]]; then
  unzip -n "$DOWNLOADS_DIR/Base_Materials_NVD@10013.zip" -d "$ASSETS_DIR/base_materials"
else
  echo "Base materials pack not present; continuing without it."
fi
