# Third-Party Dependencies

This directory is the home for external dependencies and vendor assets.

Recommended structure:

- `Lightwheel_Kitchen/`: git submodule or checked-out repo
- `isaacsim/`: extracted Isaac Sim standalone
- `downloads/`: zip downloads
- `assets/`: extracted NVIDIA asset packs

Recommended submodule command:

```bash
git submodule add -f https://github.com/LightwheelAI/Lightwheel_Kitchen.git third_party/Lightwheel_Kitchen
git submodule update --init --recursive
```

Isaac Sim and NVIDIA asset packs should remain ignored and untracked.
