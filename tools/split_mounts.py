#!/usr/bin/env python3
"""Partition PRIVATE HF model plan into profile-specific repo volumes and exact file links.

CPU-only; never downloads weights. Keep outputs OFF the public repository.
"""
import argparse,json,pathlib,collections
p=argparse.ArgumentParser();p.add_argument('--model-manifest',type=pathlib.Path,required=True)
p.add_argument('--profile-map',type=pathlib.Path,required=True);p.add_argument('--out',type=pathlib.Path,required=True);args=p.parse_args()
mm=json.loads(args.model_manifest.read_text());pm=json.loads(args.profile_map.read_text())
assert len(pm['workflows'])==mm['workflows_scanned']
files={i['name']:i for i in mm['resolved']}
mounts={r['repo']:r for r in mm['repos']}
output={'version':1,'ready_for_billing':False,'image_digests':{},'profiles':{}}
for profile in ('ltx','h3','qwen','audio'):
 used={name for w in pm['workflows'] if w['profile']==profile for name in w['model_names']}
 deps=[files[name] for name in sorted(used)]
 repos=sorted({d['repo'] for d in deps})
 entries=[]
 for item in deps:
  assert item['revision']==mounts[item['repo']]['revision']
  assert item['source'].startswith(mounts[item['repo']]['mount_path']+'/')
  entries.append({key:item[key] for key in ('name','filename','category','target','source','repo','repo_file','revision')})
 configured=[]
 for repo in repos:
  m=mounts[repo]
  configured.append({k:m[k] for k in ('repo','revision','mount_path','read_only')})
 output['profiles'][profile]={'model_files':entries,'model_mounts':configured,
        'weight_count':len(entries),'repo_count':len(configured),'cuda_validated':False,'image_digest':None}
 assert len(entries)==len(used)
print('PROFILE SPLIT',[(k,v['weight_count'],v['repo_count']) for k,v in output['profiles'].items()])
# Same weight may legitimately be mounted by multiple profiles; no duplication into private bucket.
args.out.parent.mkdir(parents=True,exist_ok=True)
args.out.write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n');args.out.chmod(0o640)
