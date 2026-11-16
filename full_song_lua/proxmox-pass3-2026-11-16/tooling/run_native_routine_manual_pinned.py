import hashlib,json,pathlib,shutil,subprocess,sys
ROOT=pathlib.Path('/opt/song-lua-audit');OUT=ROOT/'pass3-native-routine-manual-pinned';assert not OUT.exists();OUT.mkdir()
proof=json.loads((ROOT/'pass3-oracle-pins/build-proof.json').read_text());native=ROOT/'routine-native';harness=ROOT/'bin/itgmania-harness-pass3-oracle-pins'
def sha(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(native/'ITGmania-harness-trace')==proof['native_binary_sha256'] and sha(harness)==proof['harness_binary_sha256']
sys.path.insert(0,str(ROOT));import worker_pass2 as w
w.RESULTS=OUT;w.write(OUT/'source-proof.json',proof)
inputs=ROOT/'routine-manual-inputs';dest=ROOT/'Songs/__pass3_controls/routine-manual';assert dest.exists()
for file in inputs.rglob('*'):
 if file.is_file():assert sha(file)==sha(dest/file.relative_to(inputs))
jobs=json.loads((inputs/'jobs.json').read_text())
for job in jobs:
 case=OUT/job['id'];case.mkdir()
 simfile=ROOT/'Songs'/job['source_simfile'];assert sha(simfile)==job['simfile_sha256']
 result={'id':job['id'],'profile':job,'source_simfile':job['source_simfile'],'source_snapshot':proof,
  'status':'running','started_at':w.now(),'stages':{}}
 w.write(case/'result.json',result)
 argv=[harness,'song-lua-trace',simfile,'--itgmania-bin',native/'ITGmania-harness-trace',
  '--fallback-theme','Harness Simply Love','--headless','--game',job['game'],'--style',job['style'],
  '--difficulty',job['difficulty'],'--chart-index',str(job['chart_index']),'--until-gameplay-end',
  '--capture-fps','60','--max-events','250000','--timeout','180','--out',case/'native.json']
 if not job.get('autoplay',True):argv+=['--autoplay','0','--input-script',str(ROOT/'Songs'/job['input_script'])]
 if job.get('player_options'):argv+=['--player-options',job['player_options']]
 stage=w.execute(case,'capture',argv,270,memory='6G');result['stages']['capture']=stage
 if stage['exit']==0:
  summary=w.document_summary(case/'native.json');source=summary['input']['native_source']
  assert source['revision']==proof['source']['candidate_commit'] and source['modified_src'] is False
  assert summary['completion']['reason']=='gameplay-exit'
  result['native']=summary;result['status']='native_capture_pass'
  result['trace_sha256']=sha(case/'native.json')
  trace=json.loads((case/'native.json').read_text())
  assert trace['harness_version']=='0.1.102'
  events=trace['input_events'];assert len(events)==8
  assert sum(e['event']['type']=='InputEventType_FirstPress' for e in events)==4
  assert sum(e['event']['type']=='InputEventType_Release' for e in events)==4
  final=[e['args'][1] for e in trace['events'] if e.get('operation')=='MessageManager.Broadcast'
   and e.get('args',[None])[0]=='RoutineStatistics' and e['args'][1].get('phase')=='finished']
  assert len(final)==1,final
  expected={'p1':{'actual':10,'possible':10,'combo':2,'maximum':2,'w1':2,'miss':0},
   'p2':{'actual':-2,'possible':15,'combo':1,'maximum':1,'w1':2,'miss':1},
   'team':{'actual':8,'possible':25,'combo':2,'maximum':0,'w1':4,'miss':1}}
  for owner,values in expected.items():
   for key,value in values.items():assert final[0][owner][key]==value,(owner,key,final)
  assert abs(final[0]['team']['percent']-0.32)<1e-6
  result['manual_input_validation']={'native_input_events':len(events),'final_statistics':final[0],
   'assertions':'Four scored presses and four releases; P2 miss resets shared combo before subsequent P1/P2 hits; team stats distinct from participant stats.'}
  w.write(case/'manual-input-validation.json',result['manual_input_validation'])
 else:
  log=(case/'capture.log').read_text(errors='replace');result['status']=w.failure_category('capture',stage,log);result['reason']=log[-8000:]
  artifact,facts=w.preserve_diagnostics(case);result['native_failure']=facts
  if artifact:result['artifacts']=[artifact]
 result['finished_at']=w.now();w.write(case/'result.json',result)
 print(json.dumps({'id':result['id'],'status':result['status']}),flush=True)
