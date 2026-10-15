# Architecture and guarantees

```
GitHub public source repo                         Hugging Face Hub
  GitHub Actions (CPU-only on manual click)         publisher model repos
    buildx: core (ComfyUI+PyTorch)                   read-only immutable pins
     ├── ltx (LTXVideo/MSR V2/Pose)                   │
     ├── h3 (MiniMax H3/Veda/SeedVR2/FaceRefine)       │
     ├── qwen (versioned H3-family extension)          │
     └── audio (versioned H3-family extension)         │
      ↓ publish OCI image to GHCR (no model weights)  │
                ↓                                    │
        HF bridge on Empower: GPU launch disabled until vetted
                ↓ Generate (later, with budget/timeout and root approval)
        HF Jobs: pull OCI digest + mount HF repos lazily
                ↓ perform ComfyUI workflow; output to private HF bucket
        Job terminates; no idle GPU
```

## Existing local system

The canonical ComfyUI editor and its CPU-only orchestration live on Empower. Modal production workers are separate and remain unaffected. The HF bridge already exists, but `launch_enabled=false` and `image=null`. This repository is **a future versioned image build source**, not production deployment. GitHub registry creation/publication requires GitHub authorization and a manual Actions run. GHCR packages often start private: explicitly make the OCI package **public** and verify anonymous pull before considering HF Jobs.

## Profiles and future installations

- Same ComfyUI core commit for all profiles; source SHAs, Python dependencies and image recipe versioned in Git.
- Existing workflow with installed node dependencies and a different model/LoRA: **no image rebuild**, only carefully update pinned HF Hub manifest and bridge routing.
- New custom node or dependency: **edit source-pinned profile and manually rebuild that profile**, promote only validated immutable digest. Existing profiles/digests remain unchanged.
- Incompatible Python/Torch/CUDA dependency: make a **new profile**, rather than changing stable runtimes.
- Workflows live in the private on-Empower user area; they must not be committed to public GitHub. Model weights are referenced from author-owned HF repositories via read-only mounts. Read-only mounts lazily fetch files, so cold-start wall time and temporarily billed GPU Starting time may differ from Modal Volume.
- **No local custom extension code is included yet:** the Modal H3 worker references local `ComfyUI-H3-PersonMask` and `ComfyUI-YuE2-Instrumental` sources. Their distribution/license/ownership must be approved before a public image can include them. H3 and Audio build targets are not yet complete production replacements until verified.
- `Audio` has a separate extensible tag despite initially inheriting the H3 stack. `QWEN21` gets a separate tag despite initially inheriting H3; decouple deps when needed. `Vectors` remain CPU-only and `Archive` are not auto-routed to paid GPU.

## Cost and security

- GitHub Actions workflow can be started **only manually**; default public standard GitHub-hosted CPU runners are free under the published GitHub program, subject to current terms. The prebuilt PyTorch CUDA image may exceed the **~14 GiB disk** of GitHub standard runners; actual image build/push is therefore **unverified** and may need a capacity alternative. Do NOT run buildx on Empower/Lover: disk is constrained.
- Image builds are software-install operations **before any HF GPU Job**. Neither selecting a provider nor building an OCI image enables HF GPU inference. No perpetual HF GPU worker; no autoscaled warm container. HF Jobs charges may apply from `Starting`, including lazy model reads, through termination.
- No checkpoint files, input/output files, account IDs, SSH keys or API secrets in public Git. No secrets baked as Docker `ARG` / `ENV`. The only registry authentication is ephemeral `GITHUB_TOKEN` used inside the GitHub Actions workflow.
- No scheduled builds or auto-push triggers. `workflow_dispatch` only. No integration tests involving actual GPU without explicit operator-approved cost cap.
- Promote only `ghcr.io/xcentralbox/comfyui-<profile>@sha256:<digest>` after verifying an **anonymous image pull**, image entrypoint dependencies, model mount targets, exact node registration, budget and cancellation. Never use mutable `latest` for production.

## Verification state as of 2026-10-15

LTX `ghcr.io/xcentralbox/comfyui-ltx@sha256:2fb33e0935d5162f4bae8649e18207b4c68df3391284771671c21eef4c917a73` was published and CPU-validated in GitHub Actions run `38709334990`: actual ComfyUI start, package imports, mandatory MSR/LTX node registration and stop all passed, entirely without GPU. **This is not HF CUDA validation** and does not enable production. Other profiles remain unbuilt.
