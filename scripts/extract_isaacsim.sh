#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"
DOWNLOADS_DIR="$ROOT_DIR/third_party/downloads"
ISAACSIM_DIR="$ROOT_DIR/third_party/isaacsim"

mkdir -p "$ISAACSIM_DIR"
unzip -n "$DOWNLOADS_DIR/isaac-sim-standalone-5.0.0-linux-x86_64.zip" -d "$ISAACSIM_DIR"
