#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"
LIGHTWHEEL_DIR="$ROOT_DIR/third_party/Lightwheel_Kitchen"
LIGHTWHEEL_ZIP="$LIGHTWHEEL_DIR/Lightwheel_Kitchen.zip"
STAGE_USD="$LIGHTWHEEL_DIR/Collected_KitchenRoom/KitchenRoom.usd"
PROP_USD="$LIGHTWHEEL_DIR/Collected_KitchenRoom/Kitchen_Other/Kitchen_Bottle.usd"
LEGACY_STAGE_USD="$ROOT_DIR/third_party/assets/lightwheel_kitchen/Collected_KitchenRoom/KitchenRoom.usd"
LEGACY_PROP_USD="$ROOT_DIR/third_party/assets/lightwheel_kitchen/Collected_KitchenRoom/Kitchen_Other/Kitchen_Bottle.usd"

mkdir -p "$LIGHTWHEEL_DIR"

if [[ -f "$STAGE_USD" && -f "$PROP_USD" ]]; then
  printf 'LIGHTWHEEL_STAGE_USD=%q\n' "$STAGE_USD"
  printf 'LIGHTWHEEL_PROP_USD=%q\n' "$PROP_USD"
  exit 0
fi

if [[ -f "$LIGHTWHEEL_ZIP" ]]; then
  unzip -n "$LIGHTWHEEL_ZIP" -d "$LIGHTWHEEL_DIR" >/dev/null
fi

if [[ -f "$STAGE_USD" && -f "$PROP_USD" ]]; then
  printf 'LIGHTWHEEL_STAGE_USD=%q\n' "$STAGE_USD"
  printf 'LIGHTWHEEL_PROP_USD=%q\n' "$PROP_USD"
  exit 0
fi

if [[ -f "$LEGACY_STAGE_USD" && -f "$LEGACY_PROP_USD" ]]; then
  printf 'LIGHTWHEEL_STAGE_USD=%q\n' "$LEGACY_STAGE_USD"
  printf 'LIGHTWHEEL_PROP_USD=%q\n' "$LEGACY_PROP_USD"
  exit 0
fi

echo "Lightwheel Kitchen assets are missing." >&2
echo "Expected one of:" >&2
echo "  $STAGE_USD" >&2
echo "  $LEGACY_STAGE_USD" >&2
echo "Or an archive at:" >&2
echo "  $LIGHTWHEEL_ZIP" >&2
exit 2
