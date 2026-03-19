#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image

from isaacsim import SimulationApp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset-root", required=True)
    parser.add_argument("--frames-dir", required=True)
    parser.add_argument("--variant", choices=["island", "galley"], default="island")
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


def add_prop(path: str, prim_path: str, position: np.ndarray) -> None:
    from isaacsim.core.prims import SingleXFormPrim
    from isaacsim.core.utils.stage import add_reference_to_stage

    add_reference_to_stage(path, prim_path)
    SingleXFormPrim(prim_path=prim_path, name=prim_path.rsplit("/", 1)[-1], position=position)


def main() -> int:
    args = parse_args()
    frames_dir = Path(args.frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)

    simulation_app = SimulationApp({"headless": True})

    import omni.usd
    from pxr import Gf, UsdLux
    from isaacsim.core.api import World
    from isaacsim.core.api.objects import FixedCuboid
    from isaacsim.core.utils.viewports import set_camera_view
    from isaacsim.sensors.camera import Camera

    world = World(stage_units_in_meters=1.0)
    stage = omni.usd.get_context().get_stage()

    dome = UsdLux.DomeLight.Define(stage, "/World/DomeLight")
    dome.CreateIntensityAttr(80.0)
    dome.CreateColorAttr(Gf.Vec3f(0.82, 0.85, 0.90))

    key = UsdLux.SphereLight.Define(stage, "/World/KeyLight")
    key.CreateIntensityAttr(2500.0)
    key.CreateRadiusAttr(0.25)
    key.AddTranslateOp().Set(Gf.Vec3d(-1.6, -1.4, 3.4))
    key.CreateColorAttr(Gf.Vec3f(1.0, 0.95, 0.90))

    sun = UsdLux.DistantLight.Define(stage, "/World/SunLight")
    sun.CreateIntensityAttr(2200.0)
    sun.CreateColorAttr(Gf.Vec3f(0.96, 0.97, 1.0))
    sun.AddRotateXYZOp().Set(Gf.Vec3f(315.0, 0.0, 225.0))

    floor_color = np.array([0.46, 0.39, 0.32], dtype=np.float64)
    wall_color = np.array([0.82, 0.80, 0.74], dtype=np.float64)
    counter_color = np.array([0.70, 0.74, 0.80], dtype=np.float64)
    accent_color = np.array([0.22, 0.42, 0.60], dtype=np.float64)

    world.scene.add(
        FixedCuboid(
            prim_path="/World/Floor",
            name="floor",
            position=np.array([0.0, 0.0, -0.02], dtype=np.float64),
            scale=np.array([4.6, 4.6, 0.04], dtype=np.float64),
            size=1.0,
            color=floor_color,
        )
    )
    world.scene.add(
        FixedCuboid(
            prim_path="/World/BackWall",
            name="back_wall",
            position=np.array([0.0, 1.6, 1.15], dtype=np.float64),
            scale=np.array([4.6, 0.05, 2.3], dtype=np.float64),
            size=1.0,
            color=wall_color,
        )
    )
    world.scene.add(
        FixedCuboid(
            prim_path="/World/SideWall",
            name="side_wall",
            position=np.array([-1.7, 0.0, 1.15], dtype=np.float64),
            scale=np.array([0.05, 3.3, 2.3], dtype=np.float64),
            size=1.0,
            color=wall_color,
        )
    )

    if args.variant == "island":
        world.scene.add(
            FixedCuboid(
                prim_path="/World/BackCounter",
                name="back_counter",
                position=np.array([0.0, 1.08, 0.46], dtype=np.float64),
                scale=np.array([2.8, 0.78, 0.92], dtype=np.float64),
                size=1.0,
                color=counter_color,
            )
        )
        world.scene.add(
            FixedCuboid(
                prim_path="/World/Island",
                name="island",
                position=np.array([0.25, 0.05, 0.46], dtype=np.float64),
                scale=np.array([1.4, 0.86, 0.92], dtype=np.float64),
                size=1.0,
                color=accent_color,
            )
        )
        prop_positions = {
            "bottle": np.array([0.52, 0.12, 2.12], dtype=np.float64),
            "jar": np.array([0.10, 0.12, 2.12], dtype=np.float64),
            "pot": np.array([-0.55, 1.10, 2.12], dtype=np.float64),
        }
        eye_start = np.array([-2.05, -1.48, 2.20], dtype=np.float64)
        eye_end = np.array([-1.60, -1.18, 2.10], dtype=np.float64)
        target = np.array([0.15, 0.38, 0.98], dtype=np.float64)
    else:
        world.scene.add(
            FixedCuboid(
                prim_path="/World/LeftCounter",
                name="left_counter",
                position=np.array([-0.78, 0.78, 0.46], dtype=np.float64),
                scale=np.array([1.25, 0.78, 0.92], dtype=np.float64),
                size=1.0,
                color=counter_color,
            )
        )
        world.scene.add(
            FixedCuboid(
                prim_path="/World/RightCounter",
                name="right_counter",
                position=np.array([0.62, 0.18, 0.46], dtype=np.float64),
                scale=np.array([0.82, 1.95, 0.92], dtype=np.float64),
                size=1.0,
                color=accent_color,
            )
        )
        prop_positions = {
            "bottle": np.array([0.58, 0.56, 2.12], dtype=np.float64),
            "jar": np.array([0.58, -0.24, 2.12], dtype=np.float64),
            "pot": np.array([-0.90, 0.80, 2.12], dtype=np.float64),
        }
        eye_start = np.array([-2.00, -1.10, 2.12], dtype=np.float64)
        eye_end = np.array([-1.55, -0.82, 2.04], dtype=np.float64)
        target = np.array([-0.02, 0.52, 1.00], dtype=np.float64)

    asset_root = Path(args.asset_root)
    add_prop(str(asset_root / "Kitchen_Other/Kitchen_Bottle.usd"), "/World/Bottle", prop_positions["bottle"])
    add_prop(
        str(asset_root / "InteractiveAsset/SM_P_Flavour_02/Collected_SM_P_Flavour_02/Props/SM_P_Jar_01.usd"),
        "/World/Jar",
        prop_positions["jar"],
    )
    add_prop(str(asset_root / "Pot057/Pot057.usd"), "/World/Pot", prop_positions["pot"])

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

    print(f"variant={args.variant}")
    print(f"camera_eye_start={eye_start.tolist()}")
    print(f"camera_eye_end={eye_end.tolist()}")
    print(f"camera_target={target.tolist()}")
    for key, value in prop_positions.items():
        print(f"{key}_position={value.tolist()}")

    saved_frames = 0
    for frame_idx in range(args.max_frames):
        alpha = 0.0 if args.max_frames <= 1 else frame_idx / float(args.max_frames - 1)
        eye = (1.0 - alpha) * eye_start + alpha * eye_end
        set_camera_view(eye=eye, target=target, camera_prim_path="/World/benchmark_camera")
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
