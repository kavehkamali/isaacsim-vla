#!/usr/bin/env python3
from __future__ import annotations

import argparse
import numpy as np

from isaacsim import SimulationApp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage-usd", required=True)
    args, _ = parser.parse_known_args()
    return args


def compute_root_bounds(stage: object) -> tuple[np.ndarray, np.ndarray, str]:
    from pxr import Usd, UsdGeom

    default_prim = stage.GetDefaultPrim()
    if default_prim and default_prim.IsValid():
        root_prim = default_prim
    else:
        children = [child for child in stage.GetPseudoRoot().GetChildren() if child.IsValid()]
        if not children:
            raise RuntimeError("Opened stage has no valid child prims")
        root_prim = children[0]

    bbox_cache = UsdGeom.BBoxCache(
        Usd.TimeCode.Default(),
        includedPurposes=[UsdGeom.Tokens.default_, UsdGeom.Tokens.render, UsdGeom.Tokens.proxy],
    )
    world_bbox = bbox_cache.ComputeWorldBound(root_prim)
    aligned = world_bbox.ComputeAlignedRange()
    if aligned.IsEmpty():
        raise RuntimeError(f"Stage bounds for {root_prim.GetPath()} are empty")

    min_pt = aligned.GetMin()
    max_pt = aligned.GetMax()
    min_np = np.array([min_pt[0], min_pt[1], min_pt[2]], dtype=np.float64)
    max_np = np.array([max_pt[0], max_pt[1], max_pt[2]], dtype=np.float64)
    return min_np, max_np, root_prim.GetPath().pathString


def build_camera_path(min_pt: np.ndarray, max_pt: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    center = (min_pt + max_pt) / 2.0
    size = np.maximum(max_pt - min_pt, np.array([1.0, 1.0, 1.0], dtype=np.float64))

    width = max(size[0], 1.5)
    depth = max(size[1], 1.0)
    height = max(size[2], 1.0)

    target = np.array(
        [
            center[0],
            min_pt[1] + 0.30 * depth,
            min_pt[2] + 0.38 * height,
        ],
        dtype=np.float64,
    )
    eye = np.array(
        [
            center[0] + 0.20 * width,
            min_pt[1] - 0.38 * depth - 0.6,
            min_pt[2] + 0.58 * height + 0.5,
        ],
        dtype=np.float64,
    )
    return eye, target


def main() -> int:
    args = parse_args()
    simulation_app = SimulationApp({"headless": False})

    import omni.usd
    from isaacsim.core.utils.stage import is_stage_loading, open_stage
    from isaacsim.core.utils.viewports import set_camera_view

    if not open_stage(args.stage_usd):
        raise RuntimeError(f"Failed to open stage {args.stage_usd}")

    for _ in range(2400):
        simulation_app.update()
        if not is_stage_loading():
            break

    stage = omni.usd.get_context().get_stage()
    min_pt, max_pt, root_path = compute_root_bounds(stage)
    eye, target = build_camera_path(min_pt, max_pt)

    for _ in range(30):
        set_camera_view(eye=eye, target=target, camera_prim_path="/OmniverseKit_Persp")
        simulation_app.update()

    print(f"opened_stage={args.stage_usd}")
    print(f"stage_root={root_path}")
    print(f"stage_bounds_min={min_pt.tolist()}")
    print(f"stage_bounds_max={max_pt.tolist()}")
    print(f"viewport_eye={eye.tolist()}")
    print(f"viewport_target={target.tolist()}")
    print("Isaac Sim GUI is ready. Close the window to exit.")

    while simulation_app.is_running():
        simulation_app.update()

    simulation_app.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
