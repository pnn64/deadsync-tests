import datetime,hashlib,json,pathlib,subprocess,zstandard
from remote import WORK
def read(p):return json.loads(p.read_text(encoding='utf-8'))
repo=pathlib.Path('C:/GitHub/itgmania-harness');collected=WORK/'collected/1402'
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
build=read(collected/'pass3-oracle-pins/build-proof.json')
for path,digest in build['source_normalized_sha256'].items():
 assert hashlib.sha256(subprocess.check_output(['git','show',commit+':'+path],cwd=repo)).hexdigest()==digest,path
manual=[]
expected=[('start',None,0,0,0),('judgment','PlayerNumber_P1',0,0,0),('judgment','PlayerNumber_P2',5,1,0),
 ('judgment','PlayerNumber_P2',10,2,0),('judgment','PlayerNumber_P1',-2,0,1),('judgment','PlayerNumber_P2',3,1,1),('finished',None,8,2,1)]
for p in sorted((collected/'pass3-native-routine-manual-pinned').glob('*/native.json.zst')):
 with p.open('rb') as src,zstandard.ZstdDecompressor().stream_reader(src) as stream:raw=stream.read()
 trace=json.loads(raw);r=read(p.parent/'result.json');assert r['status']=='native_capture_pass'
 assert hashlib.sha256(raw).hexdigest()==r['trace_sha256']
 assert trace['harness_version']=='0.1.102' and len(trace['input_events'])==8
 observations=[e['args'][1] for e in trace['events'] if e.get('operation')=='MessageManager.Broadcast' and e.get('args',[None])[0]=='RoutineStatistics']
 assert [(v['phase'],v.get('player'),v['team']['actual'],v['team']['combo'],v['team']['miss']) for v in observations]==expected
 manual.append({'id':r['id'],'trace_sha256':r['trace_sha256'],'compressed_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
  'validation':r['manual_input_validation'],'ordered_observations':observations})
assert len(manual)==2
proof={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'harness_commit':commit,'version':'0.1.102',
 'native_commit':build['source']['candidate_commit'],'theme_commit':build['theme']['candidate_commit'],
 'native_published_branch':'https://github.com/pnn64/itgmania/tree/parity/routine-backport-20261116',
 'theme_published_branch':'https://github.com/pnn64/Simply-Love-SM5/tree/parity/pump-couple-width-20261116',
 'windows':{'passed':216,'failed':0,'ignored':5,'seconds':160.42},
 'linux':{'passed':215,'failed':0,'ignored':5,'seconds':53.69},
 'native_input_regression':{'passed':1,'failed':0,'seconds':20.33},
 'native_exact_chart_selector':{'passed':1,'failed':0,'seconds':30.39},
 'build_proof':build,'manual_controls':manual,'scope':'Native-only scoring controls; DeadSync routine parity is still failing.'}
(WORK/'oracle-pins-validation.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
baselines=[]
for p in sorted((collected/'pass3-routine-baseline-results').glob('*/result.json')):
 r=read(p);c=r.get('comparison',{})
 baselines.append({'id':r['id'],'status':r['status'],'harness_version':r['native']['harness_version'],'mismatches':c.get('mismatch_count'),
 'errors':c.get('error_count'),'mismatch_fields':c.get('mismatch_fields'),'callback_errors':c.get('errors'),
 'first_mismatches':c.get('first_mismatches',[])[:3],'source_simfile':r['source_simfile'],'evidence_path':p.relative_to(WORK/'collected').as_posix()})
assert len(baselines)==5 and sum(r['status']=='pass' for r in baselines)==1
(WORK/'routine-baseline-summary.json').write_text(json.dumps(baselines,indent=2)+'\n',encoding='utf-8')
for name in ['native-routine-backport.json','theme-pump-couple.json']:
 p=WORK/name;v=read(p);v.update(status='published and pinned by harness 0.1.102 after native validation',harness_commit=commit,validation='oracle-pins-validation.json')
 p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{k:r[k] for k in ['id','status','mismatches','errors','mismatch_fields']} for r in baselines]))
