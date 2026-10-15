# ComfyUI → Hugging Face Jobs: extensible runtime images

**Status: LTX OCI image published and CPU-verified; HF GPU inference NOT TESTED/NOT ENABLED.** This is the proposed public source repo for `xcentralbox/gen-models-hf-runtime`. It does **not** include any paid HF GPU launches or model weights. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Profiles

| Target | Purpose | Verification status |
|---|---|---|
| `core` | Shared PyTorch/CUDA + ComfyUI v0.39.2 | Source only |
| `ltx` | LTX-2.5/MSR V2/DWPose | GHCR image built, CPU-only ComfyUI+MSR verified; GPU inference NOT tested |
| `h3` | MiniMax H3/SeedVR2/Veda/FaceRefine | Source only, missing local proprietary overlay |
| `qwen` | Qwen Image 2.1 | Source only, separate tag for future dependencies |
| `audio` | Audio/YuE2 | Source only, missing local private YuE2 extension |

`Dockerfile` uses multi-stage targets sharing a common ComfyUI base; no model checkpoints are built in. Upstream repository commits match the existing operational Modal workers. `tools/validate.py` provides offline no-GPU static checks.

## GitHub publication (not yet performed)

1. Create a **public** empty `xcentralbox/gen-models-hf-runtime` GitHub repository or authorize Empower's GitHub access. Never upload the user's complete private ComfyUI worktree to this public repository.
2. Push this sanitized project from Empower, then run **Actions → Build preinstalled ComfyUI GPU images → Run workflow** with `profile=ltx` manually. No automatic GPU build/test is configured. The standard hosted runner may be too small for a CUDA/PyTorch image; do not assume it will work until proven.
3. GHCR image package is often initially private: make `comfyui-ltx` package public in GitHub settings, then confirm public unauthenticated image pull. Record the **immutable digest**, not only a tag.
4. Repeat for `h3`, `qwen`, `audio` after validating custom node dependencies and public code license. **Do not enable HF GPU production** until per-profile CUDA/ComfyUI smoke passes with explicit budget permission.

## Provenance

Validated against live Empower worker sources on 2026-10-15. The previous Lover Docker Space prototype was not built. All HF output, token handling, private model manifest, workflow state and bridge secrets remain on Empower and HF's private bucket; they are not shipped in this repository.

## 2026-10-15 — published image CPU-only verification

- GitHub CI: [`Verify published LTX OCI image`](https://github.com/xcentralbox/gen-models-hf-runtime/actions/runs/38709334990), **completed/success**, full job 7m33s.
- The test pulled the **existing, immutable** `ghcr.io/xcentralbox/comfyui-ltx@sha256:2fb33e0935d5162f4bae8649e18207b4c68df3391284771671c21eef4c917a73` on a disposable standard GitHub CPU runner. It did not build a new image or start HF Jobs.
- PyTorch/LTX Python imports succeeded with CUDA unavailable. Actual ComfyUI `--cpu` server passed `/system_stats`, and `/object_info` contained mandatory MSR/LTX classes (`ComfyUILTX25MSRICLoRALoader`, `ComfyUILTX25MSRMultiReferenceGuide`, `LTXVLatentUpsampler`, audio VAE, etc.). Container cleaned up.
- The image is **~10.22 GiB compressed**. The GitHub CPU test took **4m24s just to pull** it; do not assume identical startup timing/billing on HF hardware. Future optimization candidate: `pytorch/pytorch:2.9.1-cuda12.8-cudnn9-runtime` (~4.14 GiB base versus ~8.90 GiB `-devel`), but build compatibility has not been demonstrated.
- **Not tested:** CUDA inference, full 04D/04E generation, GPU VRAM, read-only HF mounts, private bucket media, HF Job cancellation, actual HF cold-start time. Production remains disabled on Empower.
