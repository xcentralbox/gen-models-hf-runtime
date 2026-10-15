#!/usr/bin/env python3
"""Zero-network static safety checks for *experimental* universal slim Docker source."""
from pathlib import Path
import re, json
root=Path(__file__).resolve().parent.parent
s=(root/'Dockerfile.slim').read_text()
wf=(root/'.github/workflows/build-universal-slim.yml').read_text()
assert re.search(r'^FROM python:3\.12-slim AS core$',s,re.M)
assert re.search(r'^FROM core AS ltx_slim$',s,re.M)
assert re.search(r'^FROM ltx_slim AS universal_slim$',s,re.M)
assert 'download.pytorch.org/whl/cu128' in s
assert 'torch==2.9.1 torchvision==0.24.1 torchaudio==2.9.1' in s
assert "torch.version.cuda == '12.8'" in s
for phrase in ('ComfyUI-LTXVideo','ComfyUI-LTX2.5-MSR','comfyui_controlnet_aux','ComfyUI-H3-FaceRefine','ComfyUI-MiniMaxH3-Easy','ComfyUI-Spectrum-MiniMax-H3','seedvr2_videoupscaler','Veda-on-ComfyUI','Comfyui-Memory_Cleanup'):
 assert phrase in s,phrase
assert 'H3-PersonMask' in s and 'YuE2-Instrumental' in s
assert 'hf download' not in s and 'huggingface-cli download' not in s
assert 'git clone https://github.com' in s
assert "run_job(" not in s+wf
assert 'docker/build-push-action@v6' in wf
assert 'workflow_dispatch:' in wf
assert "github.event.head_commit.message == '[SLIM-OCI-BUILD]'" in wf
assert 'branches: [main]' in wf and 'build-universal-slim.yml' in wf
assert 'ghcr.io/xcentralbox/comfyui-universal-slim' in wf
assert 'Dockerfile.slim' in wf
assert 'file: ./Dockerfile.slim' in wf
assert 'target: universal_slim' in wf
assert 'timeout-minutes: 90' in wf
assert 'run_job' not in wf
old=json.loads((root/'config/profiles.json').read_text())
assert old['production_enabled'] is False
assert old['images']['ltx']['deploy_status']=='oci_cpu_verified'
print('PASS minimal Python base, pinned official CUDA torch, single combined public node stage, no HF GPU, manual or guarded one-time CPU builder')
