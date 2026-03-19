#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image

from isaacsim import SimulationApp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames-dir", required=True)
    parser.add_argument("--max-steps", type=int, default=720)
    parser.add_argument("--frame-stride", type=int, default=2)
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


def main() -> int:
    args = parse_args()
    frames_dir = Path(args.frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)

    simulation_app = SimulationApp({"headless": True})

    from isaacsim.core.api import World
    from isaacsim.core.utils.viewports import set_camera_view
    from isaacsim.robot.manipulators.examples.franka.controllers import PickPlaceController
    from isaacsim.robot.manipulators.examples.franka.tasks import PickPlace
    from isaacsim.sensors.camera import Camera

    world = World(stage_units_in_meters=1.0)
    world.add_task(PickPlace(name="benchmark_pick_place"))

    camera_width = 1280
    camera_height = 720
    camera = Camera(
        prim_path="/World/benchmark_camera",
        position=np.array([1.6, 1.3, 1.1]),
        frequency=30,
        resolution=(camera_width, camera_height),
        orientation=np.array([1.0, 0.0, 0.0, 0.0]),
    )

    world.reset()
    camera.initialize()
    camera.set_focal_length(1.8)
    set_camera_view(
        eye=np.array([1.6, 1.3, 1.1]),
        target=np.array([0.1, 0.1, 0.25]),
        camera_prim_path="/World/benchmark_camera",
    )
    world.play()
    for _ in range(10):
        world.step(render=True)

    task = world.get_task("benchmark_pick_place")
    task_params = task.get_params()
    franka = world.scene.get_object(task_params["robot_name"]["value"])
    cube_name = task_params["cube_name"]["value"]
    articulation_controller = franka.get_articulation_controller()
    controller = PickPlaceController(
        name="pick_place_controller",
        gripper=franka.gripper,
        robot_articulation=franka,
    )
    franka.gripper.set_joint_positions(franka.gripper.joint_opened_positions)

    saved_frames = 0
    done_frame = None

    for step in range(args.max_steps):
        world.step(render=True)
        observations = world.get_observations()
        cube_obs = observations[cube_name]
        actions = controller.forward(
            picking_position=cube_obs["position"],
            placing_position=cube_obs.get("target_position", task_params["target_position"]["value"]),
            current_joint_positions=observations[franka.name]["joint_positions"],
            end_effector_offset=np.array([0.0, 0.005, 0.0]),
        )
        articulation_controller.apply_action(actions)

        if step % args.frame_stride == 0:
            rgb = get_rgb_frame(camera, camera_width, camera_height)
            if rgb is not None:
                Image.fromarray(rgb).save(frames_dir / f"frame_{saved_frames:05d}.png")
                saved_frames += 1

        if controller.is_done():
            done_frame = step
            break

    for _ in range(15):
        world.step(render=True)
        rgb = get_rgb_frame(camera, camera_width, camera_height)
        if rgb is not None:
            Image.fromarray(rgb).save(frames_dir / f"frame_{saved_frames:05d}.png")
            saved_frames += 1

    print(f"saved_frames={saved_frames}")
    print(f"controller_done_step={done_frame}")

    simulation_app.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
