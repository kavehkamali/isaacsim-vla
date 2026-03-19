#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image

from isaacsim import SimulationApp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage-usd", required=True)
    parser.add_argument("--frames-dir", required=True)
    parser.add_argument("--max-frames", type=int, default=120)
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    args, _ = parser.parse_known_args()
    return args


def to_uint8(rgb: np.ndarray) -> np.ndarray:
    if rgb.dtype == np.uint8:
        return rgb
    clipped = np.clip(rgb, 0.0, 1.0)
    return (clipped * 255.0).astype(np.uint8)


def get_rgb_frame(camera: object, width: int, height: int) -> np.ndarray | None:
    rgba = np.asarray(camera.get_rgba())
    expected = width * height * 4
    if rgba.size != expected:
        return None
    if rgba.ndim == 1:
        rgba = rgba.reshape((height, width, 4))
    elif rgba.ndim == 2 and rgba.shape == (height * width, 4):
        rgba = rgba.reshape((height, width, 4))
    elif rgba.ndim != 3:
        return None
    return to_uint8(rgba[:, :, :3])


def wait_for_stage_loading(simulation_app: SimulationApp, is_stage_loading: object, max_updates: int = 1200) -> None:
    for _ in range(max_updates):
        simulation_app.update()
        if not is_stage_loading():
            return
    raise RuntimeError("Stage did not finish loading in time")


def compute_root_bounds(stage: object) -> tuple[np.ndarray, np.ndarray, str]:
    from pxr import Gf, Usd, UsdGeom

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


def build_camera_path(min_pt: np.ndarray, max_pt: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
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
    eye_start = np.array(
        [
            center[0] + 0.20 * width,
            min_pt[1] - 0.38 * depth - 0.6,
            min_pt[2] + 0.58 * height + 0.5,
        ],
        dtype=np.float64,
    )
    eye_end = np.array(
        [
            center[0] - 0.15 * width,
            min_pt[1] - 0.30 * depth - 0.6,
            min_pt[2] + 0.54 * height + 0.45,
        ],
        dtype=np.float64,
    )
    return eye_start, eye_end, target


def main() -> int:
    args = parse_args()
    frames_dir = Path(args.frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)

    simulation_app = SimulationApp({"headless": True})

    import omni.usd
    from isaacsim.core.api import World
    from isaacsim.core.utils.stage import is_stage_loading, open_stage
    from isaacsim.core.utils.viewports import set_camera_view
    from isaacsim.sensors.camera import Camera

    if not open_stage(args.stage_usd):
        raise RuntimeError(f"Failed to open stage {args.stage_usd}")

    wait_for_stage_loading(simulation_app, is_stage_loading)
    for _ in range(30):
        simulation_app.update()

    world = World(stage_units_in_meters=1.0)
    stage = omni.usd.get_context().get_stage()
    min_pt, max_pt, root_path = compute_root_bounds(stage)
    eye_start, eye_end, target = build_camera_path(min_pt, max_pt)

    print(f"stage_root={root_path}")
    print(f"stage_bounds_min={min_pt.tolist()}")
    print(f"stage_bounds_max={max_pt.tolist()}")
    print(f"camera_eye_start={eye_start.tolist()}")
    print(f"camera_eye_end={eye_end.tolist()}")
    print(f"camera_target={target.tolist()}")

    camera = Camera(
        prim_path="/World/benchmark_camera",
        position=eye_start,
        frequency=24,
        resolution=(args.width, args.height),
        orientation=np.array([1.0, 0.0, 0.0, 0.0]),
    )
    world.reset()
    camera.initialize()
    camera.set_focal_length(2.2)
    camera.set_clipping_range(0.01, 10000.0)
    camera.resume()
    world.play()

    for _ in range(30):
        set_camera_view(eye=eye_start, target=target, camera_prim_path="/World/benchmark_camera")
        world.step(render=True)

    saved_frames = 0
    for frame_idx in range(args.max_frames):
        alpha = 0.0 if args.max_frames <= 1 else frame_idx / float(args.max_frames - 1)
        eye = (1.0 - alpha) * eye_start + alpha * eye_end
        set_camera_view(eye=eye, target=target, camera_prim_path="/World/benchmark_camera")
        world.step(render=True)
        world.step(render=True)

        rgb = get_rgb_frame(camera, args.width, args.height)
        if rgb is None:
            if frame_idx == 0:
                rgba = np.asarray(camera.get_rgba())
                print(f"rgba_shape={list(rgba.shape)}")
                print(f"rgba_size={int(rgba.size)}")
            continue
        Image.fromarray(rgb).save(frames_dir / f"frame_{saved_frames:05d}.png")
        saved_frames += 1

    print(f"saved_frames={saved_frames}")

    simulation_app.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
