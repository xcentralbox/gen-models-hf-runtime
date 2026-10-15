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

## Experimental one-image slim universal build — 2026-10-15

As requested, a new **single combined** ComfyUI image based on `python:3.12-slim` is prepared in [`Dockerfile.slim`](Dockerfile.slim), with CPU-only GitHub build in [`.github/workflows/build-universal-slim.yml`](.github/workflows/build-universal-slim.yml). It installs official **PyTorch 2.9.1 + CUDA 12.8** Linux wheels, ComfyUI and the *public* LTX/H3 custom nodes before any GPU Job. This does **not** mean the final image is 40 MiB, and is distinct from the already CPU-verified LTX image.

See [`docs/SLIM-UNIVERSAL.md`](docs/SLIM-UNIVERSAL.md) for scope, known missing private-node overlays and verification requirements. **Until OCI digest is independently verified and CUDA/model tests are approved, do not enable HF production.**

### Universal slim CPU image verified

GitHub [run 38723015759](https://github.com/xcentralbox/gen-models-hf-runtime/actions/runs/38723015759) **PASSED** both GitHub CPU build and real ComfyUI CPU-startup/12-node smoke after a pinned SeedVR2 schema patch. Published immutable image: `ghcr.io/xcentralbox/comfyui-universal-slim@sha256:afca7f0ff17c32697d5959836bd0eb51915481a1e27b7b845e677532ef8a8805` (~5.624 GiB compressed). See [`config/universal-slim.json`](config/universal-slim.json) and [`docs/SLIM-UNIVERSAL.md`](docs/SLIM-UNIVERSAL.md). **No HF GPU end-to-end run has been tested or enabled**; missing local custom nodes are not publicly redistributed.

#### HF real GPU CUDA smoke proven (no model inference)

On 2026-10-15 the CPU-verified universal OCI image above passed a **single bounded paid HF Jobs NVIDIA L40S CUDA test**: Torch 2.9.1 CUDA 12.8, CUDA matmul, actual GPU ComfyUI startup, 1,165 registered node types and all 12 mandatory public family classes. HF [Job `6ad0b8e4c662881452250c66`](https://huggingface.co/jobs/Xcentralbox/6ad0b8e4c662881452250c66) completed after 98s scheduling + 35s running. **Not** a video/weight-mount/bridge production test. GPU production remains disabled; `config/universal-slim.json` distinguishes CUDA smoke from real model inference.
