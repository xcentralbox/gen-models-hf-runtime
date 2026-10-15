#!/usr/bin/env python3
"""Convert a PRIVATE Empower workflow manifest to a local profile map. No GPU/no calls.

Never check output into the PUBLIC image source repository: workflow paths may be private.
"""
import argparse,json,pathlib,collections,re
p=argparse.ArgumentParser();p.add_argument('--manifest',required=True,type=pathlib.Path)
p.add_argument('--out',required=True,type=pathlib.Path);args=p.parse_args()
root=pathlib.Path(__file__).resolve().parents[1]
config=json.loads((root/'config/profiles.json').read_text());choices={fam:name for name,meta in config['images'].items() for fam in meta['workflow_family']}
choices.update({'Vectors':'cpu_only'})
all_names={z['name'] for z in json.loads(args.manifest.read_text())['resolved']}
m=json.loads(args.manifest.read_text());result=[];summary=collections.Counter()
for w in m['workflows']:
 folder=w['file'].split('/',1)[0];archived=(folder=='Archive')
 tag='archive' if archived else choices.get(folder)
 if not tag:raise ValueError('Unclassified active workflow folder '+folder)
 refs=sorted({z['name'] for z in w['model_references']})
 unknown=sorted(set(refs)-all_names)
 if unknown:raise ValueError('Workflow model references absent from pinned manifest: '+', '.join(unknown))
 missing=config['images'].get(tag,{}).get('missing_overlays',[])
 reason=[]
 if archived:reason.append('Archived workflow: requires explicit opt-in')
 elif tag=='cpu_only':reason.append('Local CPU-only workflow; do not incur GPU fee')
 else:
  reason.extend(['OCI digest unpublished','CUDA runtime unvalidated','Model mount/VRAM unvalidated'])
  if missing:reason.append('Non-public custom nodes require approved overlay: '+', '.join(missing))
  if any('video_depth_anything' in s for s in refs):reason.append('Video Depth Anything HF alias/path unverified')
 result.append({'workflow':w['file'],'profile':tag,'model_names':refs,'model_count':len(refs),
                'hf_gpu_ready':False,'blocking_reasons':reason})
 summary[tag]+=1
payload={'version':1,'source_manifest':str(args.manifest),'production_images_built':False,
         'hf_gpu_launch_enabled':False,'profile_summary':dict(summary),'workflows':result}
assert sum(summary.values())==m['workflows_scanned']
assert summary['archive']==m['archived_workflows']
assert sum(v for k,v in summary.items() if k!='archive')==m['active_workflows']
args.out.parent.mkdir(parents=True,exist_ok=True)
args.out.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n');args.out.chmod(0o640)
print('PASS workflow profile assignment',dict(summary),'images built false, HF production disabled')
