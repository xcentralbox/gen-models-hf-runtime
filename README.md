# ComfyUI → Hugging Face Jobs: extensible runtime images

**Status: PREPARED, NOT BUILT/PUBLISHED, NOT ENABLED.** This is the proposed public source repo for `xcentralbox/comfyui-hf-runtime`. It does **not** include any paid HF GPU launches or model weights. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Profiles

| Target | Purpose | Verification status |
|---|---|---|
| `core` | Shared PyTorch/CUDA + ComfyUI v0.39.2 | Source only |
| `ltx` | LTX-2.5/MSR V2/DWPose | Source only, needs actual image build and CUDA test |
| `h3` | MiniMax H3/SeedVR2/Veda/FaceRefine | Source only, missing local proprietary overlay |
| `qwen` | Qwen Image 2.1 | Source only, separate tag for future dependencies |
| `audio` | Audio/YuE2 | Source only, missing local private YuE2 extension |

`Dockerfile` uses multi-stage targets sharing a common ComfyUI base; no model checkpoints are built in. Upstream repository commits match the existing operational Modal workers. `tools/validate.py` provides offline no-GPU static checks.

## GitHub publication (not yet performed)

1. Create a **public** empty `xcentralbox/comfyui-hf-runtime` GitHub repository or authorize Empower's GitHub access. Never upload the user's complete private ComfyUI worktree to this public repository.
2. Push this sanitized project from Empower, then run **Actions → Build preinstalled ComfyUI GPU images → Run workflow** with `profile=ltx` manually. No automatic GPU build/test is configured. The standard hosted runner may be too small for a CUDA/PyTorch image; do not assume it will work until proven.
3. GHCR image package is often initially private: make `comfyui-ltx` package public in GitHub settings, then confirm public unauthenticated image pull. Record the **immutable digest**, not only a tag.
4. Repeat for `h3`, `qwen`, `audio` after validating custom node dependencies and public code license. **Do not enable HF GPU production** until per-profile CUDA/ComfyUI smoke passes with explicit budget permission.

## Provenance

Validated against live Empower worker sources on 2026-10-15. The previous Lover Docker Space prototype was not built. All HF output, token handling, private model manifest, workflow state and bridge secrets remain on Empower and HF's private bucket; they are not shipped in this repository.
