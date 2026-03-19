#!/usr/bin/env python3
from __future__ import annotations

import argparse

from isaacsim import SimulationApp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage-usd", required=True)
    args, _ = parser.parse_known_args()
    return args


def main() -> int:
    args = parse_args()
    simulation_app = SimulationApp({"headless": False})

    from isaacsim.core.utils.stage import is_stage_loading, open_stage

    if not open_stage(args.stage_usd):
        raise RuntimeError(f"Failed to open stage {args.stage_usd}")

    for _ in range(2400):
        simulation_app.update()
        if not is_stage_loading():
            break

    print(f"opened_stage={args.stage_usd}")
    print("Isaac Sim GUI is ready. Close the window to exit.")

    while simulation_app.is_running():
        simulation_app.update()

    simulation_app.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
