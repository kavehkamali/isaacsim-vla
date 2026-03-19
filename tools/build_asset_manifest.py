#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


USD_SUFFIXES = {".usd", ".usda", ".usdc"}

CATEGORY_RULES = {
    "mugs": ("mug", "cup"),
    "countertops": ("counter", "countertop", "kitchen_island"),
    "cabinets": ("cabinet", "drawer"),
    "tables": ("table", "desk"),
    "shelves": ("shelf", "rack"),
    "small_props": ("bottle", "plate", "bowl", "food", "utensil", "kettle"),
    "rooms": ("kitchen", "room", "interior"),
}


def classify(path: Path) -> list[str]:
    key = path.as_posix().lower()
    matched = []
    for category, terms in CATEGORY_RULES.items():
        if any(term in key for term in terms):
            matched.append(category)
    return matched


def iter_usd_files(root: Path):
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            path = Path(dirpath, filename)
            if path.suffix.lower() in USD_SUFFIXES:
                yield path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", action="append", required=True, help="Asset root to scan")
    parser.add_argument("--output", required=True, help="Output JSON manifest path")
    args = parser.parse_args()

    manifest: dict[str, object] = {
        "roots": args.root,
        "categories": {name: [] for name in CATEGORY_RULES},
        "unclassified_count": 0,
    }

    seen = set()
    for root_str in args.root:
        root = Path(root_str).expanduser().resolve()
        if not root.exists():
            continue
        for path in iter_usd_files(root):
            resolved = str(path.resolve())
            if resolved in seen:
                continue
            seen.add(resolved)
            matched = classify(path)
            if not matched:
                manifest["unclassified_count"] += 1
                continue
            for category in matched:
                manifest["categories"][category].append(resolved)

    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2))

    print(f"wrote manifest: {output_path}")
    for category, items in manifest["categories"].items():
        print(f"{category}: {len(items)}")
    print(f"unclassified_count: {manifest['unclassified_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
