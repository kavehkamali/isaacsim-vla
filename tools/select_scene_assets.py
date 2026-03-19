#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path


def choose(rng: random.Random, values: list[str], count: int = 1) -> list[str]:
    if not values:
        return []
    if count >= len(values):
        return list(values)
    return rng.sample(values, count)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--scene-config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text())
    scene_config = json.loads(Path(args.scene_config).read_text())
    rng = random.Random(scene_config["randomization"]["scene_seed"])
    categories = manifest["categories"]

    selection = {
        "scene_name": scene_config["scene_name"],
        "base_template": scene_config["base_template"],
        "assets": {
            "countertops": choose(rng, categories.get("countertops", []), 1),
            "cabinets": choose(rng, categories.get("cabinets", []), 2),
            "tables": choose(rng, categories.get("tables", []), 1),
            "shelves": choose(rng, categories.get("shelves", []), 1),
            "mugs": choose(rng, categories.get("mugs", []), scene_config["randomization"]["mug_count_range"][1]),
            "small_props": choose(rng, categories.get("small_props", []), 4),
        },
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(selection, indent=2))
    print(f"wrote scene selection: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
