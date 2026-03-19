#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"
DOWNLOADS_DIR="$ROOT_DIR/third_party/downloads"
LOGS_DIR="$ROOT_DIR/logs"

echo "[downloads]"
ls -lh "$DOWNLOADS_DIR"
echo
echo "[logs]"
ls -lh "$LOGS_DIR" || true
echo
echo "[wget]"
ps -ef | grep wget | grep -v grep || true
