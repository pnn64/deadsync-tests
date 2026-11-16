import json,pathlib,shutil,sys
ROOT=pathlib.Path('/opt/song-lua-audit');OUT=ROOT/'pass3-routine-fail-results';assert not OUT.exists();OUT.mkdir()
sys.path.insert(0,str(ROOT));import worker_pass2 as w
w.RESULTS=OUT
harness=ROOT/'bin/itgmania-harness-pass3-input-clocks';runner=ROOT/'bin/full_song_lua-pass3-routine-stats'
native_proof=json.loads((ROOT/'pass3-input-clocks/build-proof.json').read_text())
runner_proof=json.loads((ROOT/'pass3-routine-stats-resume/build-proof.json').read_text())
assert w.sha(harness)==native_proof['harness_binary_sha256'] and w.sha(runner)==runner_proof['runner_sha256']
proof={'native':native_proof,'deadsync':runner_proof};w.write(OUT/'source-proof.json',proof)
origins=[ROOT/'pass3-native-routine-fail'/('routine-fail-'+game) for game in ['dance','pump']]
jobs=[json.loads((p/'result.json').read_text())['profile'] for p in origins]
by_id={p.name:p for p in origins}
for job in jobs:
 origin=by_id[job['id']];original=json.loads((origin/'result.json').read_text())
 assert original['status']=='native_capture_pass' and w.sha(origin/'native.json')==original['trace_sha256']
 case=OUT/job['id'];case.mkdir();trace=case/'trace';trace.mkdir();shutil.copy2(origin/'native.json',trace/'native.json')
 summary=w.document_summary(trace/'native.json');assert summary['harness_version']=='0.1.103'
 result={'id':job['id'],'source_simfile':job['source_simfile'],'profile':job,'source_snapshot':proof,'native':summary,
  'capture_reused':True,'native_capture':str(origin/'result.json'),'status':'running','started_at':w.now(),'stages':{}}
 w.write(case/'result.json',result)
 w.write(trace/'_semantic_manifest.json',{'fixture_schema_version':1,'oracle_schema_version':summary['schema_version'],'harness_version':summary['harness_version'],
  'itgmania':{'git_revision':summary['input']['native_source']['revision'],'git_dirty':'false'},
  'simfiles':[{'simfile':job['source_simfile'],'fixture':'native.json','title':job['title'],'status':'ok','command_observer':summary['command_observer']}]})
 result['stages']['archive']=w.execute(case,'archive',[harness,'song-lua-archive',ROOT/'Songs','--traces',trace,'--out',case/'candidate','--uncompressed','--theme-assets',ROOT/'routine-theme'],600,memory='6G')
 assert result['stages']['archive']['exit']==0,(case/'archive.log').read_text()[-3000:]
 entry=json.loads((case/'candidate/index.json').read_text())['archives'][0];candidate=case/'candidate'/entry['archive']
 result['candidate_sha256']=w.sha(candidate)
 result['stages']['replay']=w.execute(case,'replay',[runner,'--archive',candidate,'--report',case/'report.json'],240,memory='6G')
 if (case/'report.json').exists():
  result['comparison']=w.document_summary(case/'report.json',report=True)
  result['status']='pass' if result['stages']['replay']['exit']==0 and result['comparison']['archive_accepted'] and result['comparison']['mismatch_count']==0 and result['comparison']['error_count']==0 else 'parity_failure'
  if result['status']=='pass':
   result['stages']['pack']=w.execute(case,'pack',[harness,'song-lua-pack',candidate,'--report',case/'report.json','--out',case/'accepted'],180,memory='6G')
   if result['stages']['pack']['exit']:result['status']='packaging_error'
   else:
    packed=next((case/'accepted').glob('*.tar.zst'))
    result['accepted_artifact']={'file':str(packed.relative_to(OUT)),'bytes':packed.stat().st_size,'sha256':w.sha(packed),'uncompressed_sha256':result['candidate_sha256']}
  result['report']=w.compress(case/'report.json',remove=False)
 else:result.update(status='replay_error',reason=(case/'replay.log').read_text(errors='replace')[-8000:])
 result['candidate_artifact']=w.compress(candidate,remove=False)
 result['native_artifact']=w.compress(trace/'native.json',remove=False)
 result['finished_at']=w.now();w.write(case/'result.json',result)
 print(json.dumps({'id':result['id'],'status':result['status'],'mismatches':result.get('comparison',{}).get('mismatch_count'),'fields':result.get('comparison',{}).get('mismatch_fields'),'errors':result.get('comparison',{}).get('errors'),'reason':result.get('reason')}),flush=True)
