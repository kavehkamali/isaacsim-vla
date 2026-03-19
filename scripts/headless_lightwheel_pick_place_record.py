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
    parser.add_argument("--prop-usd", required=True)
    parser.add_argument("--frames-dir", required=True)
    parser.add_argument("--max-steps", type=int, default=720)
    parser.add_argument("--frame-stride", type=int, default=2)
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

    import omni.usd
    from isaacsim.core.api import World
    from isaacsim.core.api.objects import FixedCuboid
    from isaacsim.core.prims import SingleXFormPrim
    from isaacsim.core.utils.numpy.rotations import euler_angles_to_quats
    from isaacsim.core.utils.stage import add_reference_to_stage, is_stage_loading, open_stage
    from isaacsim.core.utils.viewports import set_camera_view
    from isaacsim.robot.manipulators.examples.franka import Franka
    from isaacsim.robot.manipulators.examples.franka.controllers import PickPlaceController
    from isaacsim.sensors.camera import Camera

    if not open_stage(args.stage_usd):
        raise RuntimeError(f"Failed to open stage {args.stage_usd}")

    wait_for_stage_loading(simulation_app, is_stage_loading)
    for _ in range(30):
        simulation_app.update()

    world = World(stage_units_in_meters=1.0)

    pedestal_height = 0.62
    robot_position = np.array([0.44, -0.50, pedestal_height], dtype=np.float64)
    robot_orientation = euler_angles_to_quats(np.array([0.0, 0.0, 72.0]), degrees=True)
    pick_position = np.array([0.40, -0.28, 1.18], dtype=np.float64)
    place_position = np.array([0.50, -0.24, 1.18], dtype=np.float64)
    prop_stage_offset = np.array([0.0, 0.0, 1.22], dtype=np.float64)
    prop_pick_position = pick_position + prop_stage_offset
    prop_place_position = place_position + prop_stage_offset
    prop_offset = np.array([0.0, 0.0, -0.07], dtype=np.float64)
    prop_rest_orientation = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float64)
    initial_capture_steps = 45

    pedestal = world.scene.add(
        FixedCuboid(
            prim_path="/World/FrankaBase",
            name="franka_base",
            position=np.array([robot_position[0], robot_position[1], pedestal_height / 2.0], dtype=np.float64),
            scale=np.array([0.40, 0.40, pedestal_height], dtype=np.float64),
            size=1.0,
            color=np.array([0.16, 0.18, 0.22]),
        )
    )

    franka = world.scene.add(
        Franka(
            prim_path="/World/Franka",
            name="lightwheel_franka",
            position=robot_position,
            orientation=robot_orientation,
        )
    )

    add_reference_to_stage(args.prop_usd, "/World/benchmark_prop")
    prop = SingleXFormPrim("/World/benchmark_prop", name="benchmark_prop", position=prop_pick_position)

    camera_eye_start = np.array([-0.96, -1.94, 2.34], dtype=np.float64)
    camera_eye_end = np.array([-0.56, -1.66, 2.20], dtype=np.float64)
    camera_target = np.array([0.30, -0.32, 1.28], dtype=np.float64)

    camera = Camera(
        prim_path="/World/benchmark_camera",
        position=camera_eye_start,
        frequency=24,
        resolution=(args.width, args.height),
        orientation=np.array([1.0, 0.0, 0.0, 0.0]),
    )

    world.reset()
    prop.initialize()
    camera.initialize()
    camera.set_focal_length(1.9)
    camera.set_clipping_range(0.01, 10000.0)
    camera.resume()
    world.play()

    articulation_controller = franka.get_articulation_controller()
    controller = PickPlaceController(
        name="lightwheel_pick_place_controller",
        gripper=franka.gripper,
        robot_articulation=franka,
    )
    franka.gripper.set_joint_positions(franka.gripper.joint_opened_positions)

    prop_position = prop_pick_position.copy()
    carrying = False
    released = False
    done_step = None
    saved_frames = 0
    carry_start_step = 120
    release_step = 260

    print(f"robot_position={robot_position.tolist()}")
    print(f"pedestal_height={pedestal_height}")
    print(f"pick_position={pick_position.tolist()}")
    print(f"place_position={place_position.tolist()}")
    print(f"prop_pick_position={prop_pick_position.tolist()}")
    print(f"prop_place_position={prop_place_position.tolist()}")
    print(f"camera_eye_start={camera_eye_start.tolist()}")
    print(f"camera_eye_end={camera_eye_end.tolist()}")
    print(f"camera_target={camera_target.tolist()}")
    print(f"initial_capture_steps={initial_capture_steps}")

    for lead_step in range(initial_capture_steps):
        set_camera_view(eye=camera_eye_start, target=camera_target, camera_prim_path="/World/benchmark_camera")
        prop.set_world_pose(position=prop_position, orientation=prop_rest_orientation)
        world.step(render=True)
        prop.set_world_pose(position=prop_position, orientation=prop_rest_orientation)

        if lead_step % args.frame_stride == 0:
            rgb = get_rgb_frame(camera, args.width, args.height)
            if rgb is not None:
                Image.fromarray(rgb).save(frames_dir / f"frame_{saved_frames:05d}.png")
                saved_frames += 1

    for step in range(args.max_steps):
        alpha = 0.0 if args.max_steps <= 1 else min(step / 180.0, 1.0)
        eye = (1.0 - alpha) * camera_eye_start + alpha * camera_eye_end
        set_camera_view(eye=eye, target=camera_target, camera_prim_path="/World/benchmark_camera")

        current_joint_positions = franka.get_joint_positions()
        actions = controller.forward(
            picking_position=pick_position,
            placing_position=place_position,
            current_joint_positions=current_joint_positions,
            end_effector_offset=np.array([0.0, 0.005, 0.0]),
        )
        articulation_controller.apply_action(actions)
        world.step(render=True)

        end_effector_position, end_effector_orientation = franka.end_effector.get_world_pose()

        if (not carrying) and step >= carry_start_step:
            carrying = True

        if carrying and not released:
            prop_position = np.asarray(end_effector_position) + prop_offset
            prop.set_world_pose(position=prop_position, orientation=end_effector_orientation)
            if step >= release_step:
                released = True
                carrying = False
                prop_position = prop_place_position.copy()
                prop.set_world_pose(position=prop_position, orientation=prop_rest_orientation)
        elif not released:
            prop.set_world_pose(position=prop_position, orientation=prop_rest_orientation)
        else:
            prop.set_world_pose(position=prop_position, orientation=prop_rest_orientation)

        if step % args.frame_stride == 0:
            rgb = get_rgb_frame(camera, args.width, args.height)
            if rgb is not None:
                Image.fromarray(rgb).save(frames_dir / f"frame_{saved_frames:05d}.png")
                saved_frames += 1

        if step >= release_step + 120:
            done_step = step
            break

    for _ in range(15):
        world.step(render=True)
        prop.set_world_pose(position=prop_position, orientation=prop_rest_orientation)
        rgb = get_rgb_frame(camera, args.width, args.height)
        if rgb is not None:
            Image.fromarray(rgb).save(frames_dir / f"frame_{saved_frames:05d}.png")
            saved_frames += 1

    print(f"saved_frames={saved_frames}")
    print(f"controller_done_step={done_step}")
    print(f"released={released}")
    print(f"final_prop_position={prop_position.tolist()}")

    simulation_app.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
