#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:-/home/kaveh/project/isaacsim_vla_muglift_lab_2026-03-18}"
DOWNLOADS_DIR="$ROOT_DIR/downloads"
LOGS_DIR="$ROOT_DIR/logs"

echo "[downloads]"
ls -lh "$DOWNLOADS_DIR"
echo
echo "[logs]"
ls -lh "$LOGS_DIR" || true
echo
echo "[wget]"
ps -ef | grep wget | grep -v grep || true
