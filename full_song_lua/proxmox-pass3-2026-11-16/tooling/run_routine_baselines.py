"""Fresh routine/couple controls against the latest verified DeadSync runner."""
import json,pathlib,shutil,subprocess,sys
ROOT=pathlib.Path('/opt/song-lua-audit');OUT=ROOT/'pass3-routine-baseline-results';assert not OUT.exists();OUT.mkdir()
sys.path.insert(0,str(ROOT));import worker_pass2 as w
w.RESULTS=OUT
native=ROOT/'routine-native';harness=ROOT/'bin/itgmania-harness-pass3-oracle-pins';runner=ROOT/'bin/full_song_lua-pass3-pump-game'
proof=json.loads((ROOT/'pass3-oracle-pins/build-proof.json').read_text())
runner_proof=json.loads((ROOT/'routine-baseline-runner-proof.json').read_text())
assert w.sha(native/'ITGmania-harness-trace')==proof['native_binary_sha256']
assert w.sha(harness)==proof['harness_binary_sha256'] and w.sha(runner)==runner_proof['runner_sha256']
snapshot={'native_harness':proof,'deadsync':runner_proof};w.write(OUT/'source-proof.json',snapshot)
jobs=[j for j in json.loads((ROOT/'routine-style-inputs/jobs.json').read_text()) if j['id'] in ('style-pump-couple','style-dance-routine','style-pump-routine')]
jobs+=json.loads((ROOT/'routine-manual-inputs/jobs.json').read_text())
assert len(jobs)==5
for job in jobs:
 case=OUT/job['id'];case.mkdir();trace=case/'trace';trace.mkdir()
 result={'id':job['id'],'source_simfile':job['source_simfile'],'profile':job,'source_snapshot':snapshot,'status':'running','started_at':w.now(),'stages':{}}
 w.write(case/'result.json',result)
 if job['id'].startswith('routine-manual-'):
  origin=ROOT/'pass3-native-routine-manual-pinned'/job['id'];previous=json.loads((origin/'result.json').read_text())
  assert previous['status']=='native_capture_pass' and w.sha(origin/'native.json')==previous['trace_sha256']
  shutil.copy2(origin/'native.json',trace/'native.json');result['capture_reused']=True;result['capture_record']=str(origin/'result.json')
 else:
  args=[harness,'song-lua-trace',ROOT/'Songs'/job['source_simfile'],'--itgmania-bin',native/'ITGmania-harness-trace',
   '--fallback-theme','Harness Simply Love','--headless','--game',job['game'],'--style',job['style'],
   '--difficulty',job['difficulty'],'--chart-index',str(job['chart_index']),'--until-gameplay-end','--capture-fps','60',
   '--max-events','250000','--timeout','180','--out',trace/'native.json']
  if job.get('player_options'):args+=['--player-options',job['player_options']]
  result['stages']['capture']=w.execute(case,'capture',args,270,memory='6G')
  if result['stages']['capture']['exit']:
   result.update(status='native_capture_error',reason=(case/'capture.log').read_text(errors='replace')[-8000:]);result['finished_at']=w.now();w.write(case/'result.json',result);continue
 summary=w.document_summary(trace/'native.json');assert summary['harness_version']=='0.1.102' and summary['completion']['reason']=='gameplay-exit'
 result['native']=summary;result['trace_sha256']=w.sha(trace/'native.json')
 wrapper={'fixture_schema_version':1,'oracle_schema_version':summary['schema_version'],'harness_version':summary['harness_version'],
  'itgmania':{'git_revision':summary['input']['native_source']['revision'],'git_dirty':'false'},
  'simfiles':[{'simfile':job['source_simfile'],'fixture':'native.json','title':job['title'],'status':'ok','command_observer':summary['command_observer']}]}
 w.write(trace/'_semantic_manifest.json',wrapper)
 result['stages']['archive']=w.execute(case,'archive',[harness,'song-lua-archive',ROOT/'Songs','--traces',trace,'--out',case/'candidate','--uncompressed','--theme-assets',ROOT/'routine-theme'],600,memory='6G')
 if result['stages']['archive']['exit']:
  result.update(status='archive_error',reason=(case/'archive.log').read_text(errors='replace')[-8000:])
 else:
  entry=json.loads((case/'candidate/index.json').read_text())['archives'][0];candidate=case/'candidate'/entry['archive']
  result['candidate_sha256']=w.sha(candidate)
  result['stages']['replay']=w.execute(case,'replay',[runner,'--archive',candidate,'--report',case/'report.json'],180,memory='6G')
  if (case/'report.json').exists():
   result['comparison']=w.document_summary(case/'report.json',report=True)
   result['status']='pass' if result['stages']['replay']['exit']==0 and result['comparison']['archive_accepted'] else 'parity_failure'
   if result['status']=='pass':
    result['stages']['pack']=w.execute(case,'pack',[harness,'song-lua-pack',candidate,'--report',case/'report.json','--out',case/'accepted'],180,memory='6G')
    if result['stages']['pack']['exit']:result['status']='packaging_error'
   result['report']=w.compress(case/'report.json',remove=True)
  else:result.update(status='replay_error',reason=(case/'replay.log').read_text(errors='replace')[-8000:])
  result['candidate_artifact']=w.compress(candidate,remove=True)
 result['native_artifact']=w.compress(trace/'native.json',remove=False)
 result['finished_at']=w.now();w.write(case/'result.json',result)
 print(json.dumps({'id':result['id'],'status':result['status'],'comparison':result.get('comparison'),'reason':result.get('reason')}),flush=True)
