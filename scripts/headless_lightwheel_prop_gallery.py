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
    parser.add_argument("--asset-root", required=True)
    parser.add_argument("--frames-dir", required=True)
    parser.add_argument("--max-frames", type=int, default=90)
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


def main() -> int:
    args = parse_args()
    frames_dir = Path(args.frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)

    simulation_app = SimulationApp({"headless": True})

    from isaacsim.core.api import World
    from isaacsim.core.prims import SingleXFormPrim
    from isaacsim.core.utils.stage import add_reference_to_stage, is_stage_loading, open_stage
    from isaacsim.core.utils.viewports import set_camera_view
    from isaacsim.sensors.camera import Camera

    if not open_stage(args.stage_usd):
        raise RuntimeError(f"Failed to open stage {args.stage_usd}")

    wait_for_stage_loading(simulation_app, is_stage_loading)
    for _ in range(30):
        simulation_app.update()

    world = World(stage_units_in_meters=1.0)
    asset_root = Path(args.asset_root)
    stage_offset = np.array([0.0, 0.0, 1.22], dtype=np.float64)

    # Mixed placements to visualize reachable island spots and a few alternate countertop props.
    gallery_items = [
        ("bottle_rear", asset_root / "Kitchen_Other/Kitchen_Bottle.usd", np.array([0.42, -0.30, 1.18], dtype=np.float64)),
        ("bottle_island_mid", asset_root / "Kitchen_Other/Kitchen_Bottle005.usd", np.array([0.18, -0.64, 1.18], dtype=np.float64)),
        ("bottle_island_right", asset_root / "Kitchen_Other/Kitchen_Bottle006.usd", np.array([0.34, -0.66, 1.18], dtype=np.float64)),
        (
            "jar_island_right",
            asset_root / "InteractiveAsset/SM_P_Flavour_02/Collected_SM_P_Flavour_02/Props/SM_P_Jar_01.usd",
            np.array([0.48, -0.66, 1.18], dtype=np.float64),
        ),
        ("pot_corner", asset_root / "Pot057/Pot057.usd", np.array([0.62, -0.52, 1.18], dtype=np.float64)),
    ]

    for name, usd_path, base_position in gallery_items:
        add_reference_to_stage(str(usd_path), f"/World/{name}")
        SingleXFormPrim(
            prim_path=f"/World/{name}",
            name=name,
            position=base_position + stage_offset,
        )
        print(f"{name}={usd_path}:{(base_position + stage_offset).tolist()}")

    camera_eye_start = np.array([-0.88, -2.30, 2.40], dtype=np.float64)
    camera_eye_end = np.array([-0.30, -1.85, 2.26], dtype=np.float64)
    camera_target = np.array([0.34, -0.60, 1.28], dtype=np.float64)

    camera = Camera(
        prim_path="/World/gallery_camera",
        position=camera_eye_start,
        frequency=24,
        resolution=(args.width, args.height),
        orientation=np.array([1.0, 0.0, 0.0, 0.0]),
    )

    world.reset()
    camera.initialize()
    camera.set_focal_length(1.9)
    camera.set_clipping_range(0.01, 10000.0)
    camera.resume()
    world.play()

    for _ in range(30):
        set_camera_view(eye=camera_eye_start, target=camera_target, camera_prim_path="/World/gallery_camera")
        world.step(render=True)

    saved_frames = 0
    for frame_idx in range(args.max_frames):
        alpha = 0.0 if args.max_frames <= 1 else frame_idx / float(args.max_frames - 1)
        eye = (1.0 - alpha) * camera_eye_start + alpha * camera_eye_end
        set_camera_view(eye=eye, target=camera_target, camera_prim_path="/World/gallery_camera")
        world.step(render=True)
        rgb = get_rgb_frame(camera, args.width, args.height)
        if rgb is None:
            continue
        Image.fromarray(rgb).save(frames_dir / f"frame_{saved_frames:05d}.png")
        saved_frames += 1

    print(f"saved_frames={saved_frames}")

    simulation_app.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
