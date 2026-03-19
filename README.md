# isaacsim-vla

Canonical workspace root for Isaac Sim VLA experiments.

The repo itself is the workspace. On the remote machine the intended path is:

`/home/kaveh/project/isaacsim-vla`

There should not be an extra dated outer folder.

## Layout

- `configs/`: task, scene, and policy configs
- `scripts/`: runnable shell entrypoints and headless Isaac Sim Python scripts
- `tools/`: asset manifest and scene-selection helpers
- `results/`: generated rollout videos and frame dumps
- `logs/`: download and extraction logs
- `third_party/`: Isaac Sim, downloaded asset packs, and optional external repos

## third_party Layout

- `third_party/isaacsim/`: extracted Isaac Sim standalone
- `third_party/downloads/`: downloaded Isaac Sim and NVIDIA asset zip files
- `third_party/assets/`: extracted NVIDIA asset packs such as SimReady furniture and scene templates
- `third_party/Lightwheel_Kitchen/`: recommended location for the Lightwheel Kitchen repo or submodule

Tracked source stays in git. Large binaries and extracted vendor assets stay ignored.

## Recommended External Dependencies

For Lightwheel Kitchen, use a submodule:

```bash
git submodule add -f https://github.com/LightwheelAI/Lightwheel_Kitchen.git third_party/Lightwheel_Kitchen
git submodule update --init --recursive
```

Isaac Sim is not handled as a git submodule. Keep it as an extracted vendor dependency under `third_party/isaacsim/`.

The path is ignored by default so that an existing checkout on a machine like `33` does not dirty the repo.

## Remote Setup

On `10.225.68.33` the canonical root should be:

```bash
cd /home/kaveh/project/isaacsim-vla
```

Create the expected workspace folders:

```bash
./scripts/bootstrap_remote.sh
```

That creates:

- `third_party/downloads/`
- `third_party/assets/`
- `third_party/isaacsim/`
- `third_party/Lightwheel_Kitchen/`
- `logs/`
- `results/`

## First-Time Preparation

Put Isaac Sim and NVIDIA zips into `third_party/downloads/`.

Put the Lightwheel kitchen zip at:

`third_party/Lightwheel_Kitchen/Lightwheel_Kitchen.zip`

Then run the full preparation flow:

```bash
./scripts/prepare_workspace.sh
```

That will:

- create the canonical workspace folders
- extract Isaac Sim into `third_party/isaacsim/`
- extract NVIDIA packs into `third_party/assets/`
- extract the Lightwheel kitchen zip if needed
- build `results/simready_manifest.json`
- run a preflight check so tests do not fail later from missing assets

If you only want to verify the workspace state without changing it:

```bash
./scripts/check_workspace.sh
```

If the preflight fails, fix the missing archives it names and rerun `./scripts/prepare_workspace.sh`.

## Main Runs

Recorded smoke test:

```bash
./scripts/run_recorded_smoke_test.sh
```

Lightwheel kitchen scene capture:

```bash
./scripts/run_lightwheel_scene_capture.sh
```

Lightwheel scripted pick-place:

```bash
./scripts/run_lightwheel_pick_place.sh
```

All wrappers default to:

- repo root as the workspace root
- `GPU 0` only
- `third_party/isaacsim/` for Isaac Sim
- `third_party/Lightwheel_Kitchen/` for the Lightwheel kitchen scene

The Lightwheel wrappers also auto-extract `third_party/Lightwheel_Kitchen/Lightwheel_Kitchen.zip` on first use if the kitchen USD tree is not already unpacked, but the recommended path is still to run `./scripts/prepare_workspace.sh` first.

## Config Notes

- `configs/task/mug_lift.json`: task settings and success criteria
- `configs/scenes/lightwheel_kitchen.json`: Lightwheel scene and pickable object paths
- `configs/policies/scripted.json`: current working baseline
- `configs/policies/gr00t_n15_adapter.json`: GR00T adapter scaffold only
- `configs/policies/pi05_adapter.json`: `pi0.5` adapter scaffold only

## Current Status

- The scripted Lightwheel kitchen flow is the current validated benchmark path.
- GR00T is not integrated into live control yet.
- The SimReady manifest builder is still filename-based and needs tightening before large randomized sweeps.
