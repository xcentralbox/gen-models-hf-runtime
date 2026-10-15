#!/usr/bin/env python3
"""CPU-only no-network source-level checks; NO GPU, Docker daemon or downloads."""
import argparse,json,pathlib,re,hashlib,sys
p=argparse.ArgumentParser();p.add_argument('--public',action='store_true');p.add_argument('--workflow-manifest',type=pathlib.Path);args=p.parse_args()
root=pathlib.Path(__file__).resolve().parent.parent
config=json.loads((root/'config/profiles.json').read_text());docker=(root/'Dockerfile').read_text();wf=(root/'.github/workflows/build-images.yml').read_text()
assert config['production_enabled'] is False
assert config['gpu_min_containers']==0
assert all(config['policy'].values())
assert 'workflow_dispatch:' in wf and not re.search(r'(?m)^  (push|schedule|pull_request):',wf)
assert 'packages: write' in wf and 'GITHUB_TOKEN' in wf
assert 'docker/build-push-action@v6' in wf
assert 'FROM ${TORCH_BASE} AS core' in docker
for tag,meta in config['images'].items():
 assert re.fullmatch('[a-z][a-z0-9-]+',tag)
 assert docker.count(' AS '+tag+'\n')==1,tag
 assert meta['docker_target']==tag
 assert meta['deploy_status'] in ('source_prepared_unbuilt','oci_cpu_verified')
 if meta['deploy_status']=='oci_cpu_verified':
  assert tag=='ltx' and meta.get('immutable_image','').startswith('ghcr.io/xcentralbox/comfyui-ltx@sha256:')
  assert meta.get('oci_cpu_verify_run') == 38709334990
  assert meta.get('gpu_runtime_verified') is False
 assert len(meta['workflow_family'])
assert 'git clone https://github.com/comfyanonymous/ComfyUI.git /comfyui' in docker
assert config['core_version'] in docker or ('COMFY_SHA='+config['core_version']) in docker
assert 'LTX-2.5-Licon-MSR-V2.safetensors' not in docker
assert 'pip install' not in (root/'docs/hf-job-example.py').read_text()
assert 'git clone' not in (root/'docs/hf-job-example.py').read_text()
assert 'run_job(' not in wf
assert not (root/'.env').exists()
# Never accidentally publish proprietary local overlays or private HF project state.
for banned in ('hf_jobs_token','modal_runtime.json','provider_preference.json','secrets.json','model_manifest.json','model_mount_plan.json'):
 assert not list(root.rglob(banned)),banned
allfiles=[x for x in root.rglob('*') if x.is_file() and '.git' not in x.parts]
for path in allfiles:
 rel=path.relative_to(root).as_posix()
 assert path.stat().st_size < 2_000_000,(rel,path.stat().st_size)
 assert not rel.startswith(('overlays/private','overlays/local'))
 if rel.endswith(('.py','.json','.txt','.yml','.md','Dockerfile','.gitignore','.dockerignore')):
  raw=path.read_bytes()
  assert not re.search(rb'(hf_[a-zA-Z0-9]{28,}|github_pat_[A-Za-z0-9_]+|ghp_[A-Za-z0-9]{28,})',raw),(rel,'possible secret')
  assert not re.search(rb'BEGIN (OPENSSH|RSA|EC|PRIVATE) KEY',raw),(rel,'private key')
assert not any(x.suffix.lower() in ('.safetensors','.pt','.pth','.bin','.ckpt','.gguf','.onnx','.wav','.mp4','.png') for x in allfiles)
if args.workflow_manifest:
 m=json.loads(args.workflow_manifest.read_text())
 assert m['workflows_scanned']>=87
 families={k for item in m['workflows'] if not item['file'].startswith('Archive/') for k in item['file'].split('/')[:1]}
 expected={w for meta in config['images'].values() for w in meta['workflow_family'] if w not in ['Vectors (CPU-only; HF GPU not needed)']}
 assert families.issubset(expected|{'Vectors'}),('new workflow family requires explicit classification',families-expected-{'Vectors'})
 refs={item['name'] for w in m['workflows'] for item in w['model_references']}
 assert refs.issubset({item['name'] for item in m['resolved']})
 assert len(m['resolved'])==m['unique_model_references']
 assert 0<len(refs)<=len(m['resolved'])
 print('Local manifest cover: %s workflows, %s model filenames, %s families'%(m['workflows_scanned'],len(refs),len(families)))
print('PASS: %d public source files, %d explicit profiles, manual-only CPU image builds; no models or obvious secrets'%(len(allfiles),len(config['images'])))
