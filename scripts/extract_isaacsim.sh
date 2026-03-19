#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"
DOWNLOADS_DIR="$ROOT_DIR/third_party/downloads"
ISAACSIM_DIR="$ROOT_DIR/third_party/isaacsim"
ISAACSIM_ZIP="$DOWNLOADS_DIR/isaac-sim-standalone-5.0.0-linux-x86_64.zip"

mkdir -p "$ISAACSIM_DIR"

if [[ ! -f "$ISAACSIM_ZIP" ]]; then
  echo "Missing Isaac Sim archive: $ISAACSIM_ZIP" >&2
  echo "Place the standalone zip into third_party/downloads before running this script." >&2
  exit 2
fi

unzip -n "$ISAACSIM_ZIP" -d "$ISAACSIM_DIR"
