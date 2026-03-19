#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"

"$SCRIPT_DIR/bootstrap_remote.sh" "$ROOT_DIR"
"$SCRIPT_DIR/extract_isaacsim.sh" "$ROOT_DIR"
"$SCRIPT_DIR/extract_omniverse_packs.sh" "$ROOT_DIR"
eval "$("$SCRIPT_DIR/prepare_lightwheel_kitchen.sh" "$ROOT_DIR")"
"$SCRIPT_DIR/build_simready_manifest.sh" "$ROOT_DIR"
"$SCRIPT_DIR/check_workspace.sh" "$ROOT_DIR"

echo "prepare_workspace=ok"
