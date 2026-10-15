# Build ONCE via manual GitHub Actions, never during HF Jobs Generate.
# No model weights, private workflow JSON, tokens, input/output files or HF bucket data.
# Source commits mirror the installed, clean Modal worker source trees (2026-10-15).
ARG TORCH_BASE=pytorch/pytorch:2.9.1-cuda12.8-cudnn9-devel
FROM ${TORCH_BASE} AS core
ARG COMFY_SHA=3c1b7a17fdf239d35ce98cc777756f572d089795
ENV DEBIAN_FRONTEND=noninteractive PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1 \
    COMFY_DIR=/comfyui
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ffmpeg libgl1 libglib2.0-0 libsm6 libxext6 ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY config/constraints.txt /tmp/comfy-constraints.txt
RUN git clone https://github.com/comfyanonymous/ComfyUI.git /comfyui \
    && git -C /comfyui checkout --detach ${COMFY_SHA} \
    && python -m pip install -c /tmp/comfy-constraints.txt -r /comfyui/requirements.txt \
    && python -m pip install -c /tmp/comfy-constraints.txt requests websocket-client==1.8.0 psutil
WORKDIR /comfyui
# The HF adapter explicitly runs a separate runner.py from its private HF bucket.
# An image by itself never starts any GPU inference, ComfyUI daemon or warm worker.
CMD ["python", "-c", "print('ComfyUI OCI environment ready; HF Jobs command required')"]

# LTX-2.5 / MSR V2 / DWPose profile, identical upstream source SHAs to the Modal worker.
FROM core AS ltx
RUN git clone https://github.com/Lightricks/ComfyUI-LTXVideo.git /comfyui/custom_nodes/ComfyUI-LTXVideo \
    && git -C /comfyui/custom_nodes/ComfyUI-LTXVideo checkout --detach 3bf3ca62595f1764c47d01c35c8e5dfe47e1a88f \
    && git clone https://github.com/liconstudio/ComfyUI-LTX2.5-MSR.git /comfyui/custom_nodes/ComfyUI-LTX2.5-MSR \
    && git -C /comfyui/custom_nodes/ComfyUI-LTX2.5-MSR checkout --detach 03061c18f8a79d26f3c63931dd8e28f5e5d872a6 \
    && git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git /comfyui/custom_nodes/comfyui_controlnet_aux \
    && git -C /comfyui/custom_nodes/comfyui_controlnet_aux checkout --detach a587a4c1594524c1d2de5cd1a86cd868ff448e1c \
    && python -m pip install -c /tmp/comfy-constraints.txt -r /comfyui/custom_nodes/ComfyUI-LTXVideo/requirements.txt \
    && python -m pip install -c /tmp/comfy-constraints.txt \
       onnxruntime==1.23.2 timm==1.0.20 scikit-image omegaconf==2.3.0 \
       addict==2.4.0 yacs==0.1.8 trimesh rtree albumentationsx scikit-learn mediapipe \
    && python -c "import torch, diffusers, transformers, kornia, colour, OpenImageIO, websocket; print('ltx packages', torch.__version__)"
# Pose model files are HF repo mounts, not bundled. /models/pose_preprocessors is
# not a valid default unless the bridge mounts the files there; keep ckpts fallback.
ENV AUX_ORT_PROVIDERS=CPUExecutionProvider

# MiniMax H3 / SeedVR2 / Veda / H3 FaceRefine + generic audio dependencies.
# NOTE: locally authored H3-PersonMask and YuE2-Instrumental overlays are NOT
# released here; do not mark dependent graphs verified until approved/rebuilt.
FROM core AS h3
RUN git clone https://github.com/xmarre/ComfyUI-Spectrum-MiniMax-H3.git /comfyui/custom_nodes/ComfyUI-Spectrum-MiniMax-H3 \
    && git -C /comfyui/custom_nodes/ComfyUI-Spectrum-MiniMax-H3 checkout --detach 806fe498d574a726fecb8818917f00a4b993fd77 \
    && git clone https://github.com/nkxx188/ComfyUI-MiniMaxH3-Easy.git /comfyui/custom_nodes/ComfyUI-MiniMaxH3-Easy \
    && git -C /comfyui/custom_nodes/ComfyUI-MiniMaxH3-Easy checkout --detach 23ba347cc9208641e2b5ad2cd1ed11a6363c5740 \
    && git clone https://github.com/Carasibana/ComfyUI-H3-FaceRefine.git /comfyui/custom_nodes/ComfyUI-H3-FaceRefine \
    && git -C /comfyui/custom_nodes/ComfyUI-H3-FaceRefine checkout --detach d8521d14fe0d721d80cd9417fff5a559cbc21aba \
    && git clone https://github.com/numz/ComfyUI-SeedVR2_VideoUpscaler.git /comfyui/custom_nodes/seedvr2_videoupscaler \
    && git -C /comfyui/custom_nodes/seedvr2_videoupscaler checkout --detach 4490bd1f482e026674543386bb2a4d176da245b9 \
    && git clone https://github.com/veda-sparse/Veda-on-ComfyUI.git /comfyui/custom_nodes/Veda-on-ComfyUI \
    && git -C /comfyui/custom_nodes/Veda-on-ComfyUI checkout --detach 8d7ac153ac215d636eaf1b5910b0536c3de9e6ed \
    && git clone https://github.com/LAOGOU-666/Comfyui-Memory_Cleanup.git /comfyui/custom_nodes/Comfyui-Memory_Cleanup \
    && git -C /comfyui/custom_nodes/Comfyui-Memory_Cleanup checkout --detach 58de13a6090e04408e343501ff8902c034d9f518 \
    && python -m pip install -c /tmp/comfy-constraints.txt \
       triton 'omegaconf>=2.3.0' 'diffusers>=0.33.1' 'peft>=0.17.0' \
       'rotary-embedding-torch>=0.5.3' opencv-python-headless gguf ultralytics matplotlib scipy \
    && python -m pip install -c /tmp/comfy-constraints.txt -r /comfyui/custom_nodes/ComfyUI-H3-FaceRefine/requirements.txt \
    && python -m pip install -c /tmp/comfy-constraints.txt -r /comfyui/custom_nodes/seedvr2_videoupscaler/requirements.txt \
    && python -m pip install -c /tmp/comfy-constraints.txt -r /comfyui/custom_nodes/Veda-on-ComfyUI/requirements.txt \
    && python -c "import torch, triton, diffusers, peft, cv2, gguf, ultralytics; print('h3 packages', torch.__version__)"

# Qwen-Image 2.1 has its own versioned profile and can be extended independently.
# Start with the operational H3 library stack; model weights are HF mounts.
FROM h3 AS qwen

# Audio currently reuses H3 dependencies, but custom YuE2-Instrumental code is
# deliberately NOT published to a public GHCR repo pending license/ownership check.
FROM h3 AS audio
