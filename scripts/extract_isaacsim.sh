#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:-/home/kaveh/project/isaacsim_vla_muglift_lab_2026-03-18}"
DOWNLOADS_DIR="$ROOT_DIR/downloads"
ISAACSIM_DIR="$ROOT_DIR/isaacsim"

mkdir -p "$ISAACSIM_DIR"
unzip -n "$DOWNLOADS_DIR/isaac-sim-standalone-5.0.0-linux-x86_64.zip" -d "$ISAACSIM_DIR"
