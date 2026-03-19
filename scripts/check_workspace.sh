#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"
ISAACSIM_PY="$ROOT_DIR/third_party/isaacsim/python.sh"
SCENE_TEMPLATES_DIR="$ROOT_DIR/third_party/assets/scene_templates"
SIMREADY_FURNITURE_DIR="$ROOT_DIR/third_party/assets/simready_furniture"
MANIFEST_PATH="$ROOT_DIR/results/simready_manifest.json"

missing=0

if [[ ! -x "$ISAACSIM_PY" ]]; then
  echo "missing: $ISAACSIM_PY"
  missing=1
fi

if [[ ! -d "$SCENE_TEMPLATES_DIR" ]]; then
  echo "missing: $SCENE_TEMPLATES_DIR"
  missing=1
fi

if [[ ! -d "$SIMREADY_FURNITURE_DIR" ]]; then
  echo "missing: $SIMREADY_FURNITURE_DIR"
  missing=1
fi

if [[ ! -f "$MANIFEST_PATH" ]]; then
  echo "missing: $MANIFEST_PATH"
  missing=1
fi

if eval "$("$ROOT_DIR/scripts/prepare_lightwheel_kitchen.sh" "$ROOT_DIR")"; then
  echo "lightwheel_stage: ${LIGHTWHEEL_STAGE_USD:-unknown}"
  echo "lightwheel_prop: ${LIGHTWHEEL_PROP_USD:-unknown}"
else
  missing=1
fi

if [[ "$missing" -ne 0 ]]; then
  echo "workspace_check=failed"
  exit 2
fi

echo "workspace_check=ok"
