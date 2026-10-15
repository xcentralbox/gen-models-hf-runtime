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
assert 'patches/seedvr2-cpu-schema.patch' in s
assert 'git apply --unidiff-zero --check /tmp/seedvr2-cpu-schema.patch' in s
assert 'gpu' not in (root/'patches/seedvr2-cpu-schema.patch').read_text().split('return result if result else')[-1].lower()
assert "github.event.head_commit.message == '[SLIM-OCI-FIX]'" in wf
assert 'needs.build.outputs.digest' in wf
assert 'SeedVR2LoadDiTModel' in wf
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

# Public OCI metadata is factual and does not arm any paid GPU runtime.
meta=json.loads((root/'config/universal-slim.json').read_text())
assert meta['production_enabled'] is False and meta['gpu_cuda_inference_verified'] is False
assert meta['image'].startswith('ghcr.io/xcentralbox/comfyui-universal-slim@sha256:')
assert meta['build_run_id']==38723015759 and meta['cpu_smoke_run_id']==38723015759
assert len(meta['cpu_mandatory_node_classes_verified'])==12
assert meta['cpu_test_status']=='completed_success'

assert meta['hf_cuda_smoke_verified'] is True
assert meta['hf_cuda_smoke_run']=='completed_success'
assert meta['hf_real_model_inference_verified'] is False
assert meta['hf_video_generation_verified'] is False
assert meta['hf_model_mounts_verified'] is False
