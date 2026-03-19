# isaacsim-vla

Fresh Isaac Sim workspace for headless VLA benchmarking in kitchen-style scenes, pinned to `GPU 0`.

## What This Repo Is

- A small repo that lives inside a larger remote Isaac Sim workspace.
- Focused on scripted and model-driven tabletop manipulation benchmarks.
- Built so the task harness can stay the same while the policy changes.

Current validated setup:

- Robot: Franka Panda
- Main scene: Lightwheel Kitchen
- Current working policy: scripted Isaac Sim `PickPlaceController`
- Planned policy adapters: GR00T N1.5 and `pi0.5`

## Repo Layout

- `README.md`: root runbook
- `configs/`: task, scene, and policy configs
- `scripts/`: all shell entrypoints and headless Python runners
- `tools/`: asset indexing and scene-selection helpers
- `results/`: intentionally empty in the repo; keep generated local media outside source control

All runnable scripts are under `scripts/`.

## Remote Workspace Layout

Default remote workspace root:

`/home/kaveh/project/isaacsim_vla_muglift_lab_2026-03-18`

Expected remote repo path:

`/home/kaveh/project/isaacsim_vla_muglift_lab_2026-03-18/repo/isaacsim-vla`

Important sibling directories in that remote workspace:

- `isaacsim/`: extracted Isaac Sim standalone
- `assets/`: extracted NVIDIA and Lightwheel assets
- `downloads/`: original zip downloads
- `logs/`: download and extraction logs
- `results/`: rendered frames, MP4s, and manifest outputs

## Supported Scripts

Provisioning and setup:

- `scripts/bootstrap_remote.sh`
- `scripts/check_downloads.sh`
- `scripts/extract_isaacsim.sh`
- `scripts/extract_omniverse_packs.sh`
- `scripts/build_simready_manifest.sh`

Benchmark and recording entrypoints:

- `scripts/run_smoke_pick_place.sh`
- `scripts/run_recorded_smoke_test.sh`
- `scripts/run_lightwheel_scene_capture.sh`
- `scripts/run_lightwheel_pick_place.sh`

Internal headless runners:

- `scripts/headless_pick_place_record.py`
- `scripts/headless_lightwheel_scene_record.py`
- `scripts/headless_lightwheel_pick_place_record.py`
- `scripts/headless_lightwheel_prop_gallery.py`
- `scripts/headless_synthetic_counter_scene_record.py`

## Quick Start On The Remote Machine

SSH to the workstation and go to the repo:

```bash
ssh home-linux-33
cd /home/kaveh/project/isaacsim_vla_muglift_lab_2026-03-18/repo/isaacsim-vla
```

Prepare the remote workspace:

```bash
./scripts/bootstrap_remote.sh
./scripts/check_downloads.sh
./scripts/extract_isaacsim.sh
./scripts/extract_omniverse_packs.sh
./scripts/build_simready_manifest.sh
```

Run the Isaac Sim smoke test with recording:

```bash
./scripts/run_recorded_smoke_test.sh
```

Capture the Lightwheel kitchen scene video:

```bash
./scripts/run_lightwheel_scene_capture.sh
```

Run the current scripted Lightwheel pick-place benchmark:

```bash
./scripts/run_lightwheel_pick_place.sh
```

Each run writes frames and the encoded MP4 under the remote workspace `results/` directory.

## Key Script Arguments

Most wrappers accept the remote workspace root as the first argument.

Examples:

```bash
./scripts/run_lightwheel_scene_capture.sh /home/kaveh/project/isaacsim_vla_muglift_lab_2026-03-18
./scripts/run_lightwheel_pick_place.sh /home/kaveh/project/isaacsim_vla_muglift_lab_2026-03-18
./scripts/run_lightwheel_pick_place.sh \
  /home/kaveh/project/isaacsim_vla_muglift_lab_2026-03-18 \
  /home/kaveh/project/isaacsim_vla_muglift_lab_2026-03-18/assets/lightwheel_kitchen/Collected_KitchenRoom/KitchenRoom.usd \
  /home/kaveh/project/isaacsim_vla_muglift_lab_2026-03-18/assets/lightwheel_kitchen/Collected_KitchenRoom/Kitchen_Other/Kitchen_Bottle.usd
```

## Configs

- `configs/task/mug_lift.json`: task-level control, success, and camera settings
- `configs/scenes/lightwheel_kitchen.json`: current Lightwheel kitchen scene and pickable assets
- `configs/scenes/simready_countertop_a.json`
- `configs/scenes/simready_countertop_b.json`
- `configs/policies/scripted.json`: current working baseline
- `configs/policies/gr00t_n15_adapter.json`: GR00T adapter scaffold only
- `configs/policies/pi05_adapter.json`: `pi0.5` adapter scaffold only

## Current Status

- All Isaac Sim runs are pinned to `GPU 0`.
- The validated benchmark path today is the scripted Lightwheel kitchen pick-place flow.
- GR00T is not wired into live control yet; only the adapter config surface exists.
- The SimReady manifest builder is still filename-based and should be tightened before relying on it for large randomized mug sweeps.

## Notes

- This repo intentionally keeps generated local videos and previews out of source control.
- The remote workspace is the source of truth for heavy assets and rendered outputs.
