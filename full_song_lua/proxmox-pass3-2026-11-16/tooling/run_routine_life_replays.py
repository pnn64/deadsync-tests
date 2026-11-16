import json,pathlib,sys,zstandard
ROOT=pathlib.Path('/opt/song-lua-audit');OUT=ROOT/'pass3-routine-life-results'
assert not OUT.exists();OUT.mkdir()
sys.path.insert(0,str(ROOT));import worker_pass2 as w
w.RESULTS=OUT
runner=ROOT/'bin/full_song_lua-pass3-routine-life'
harness=ROOT/'bin/itgmania-harness-pass3-input-clocks'
proof=json.loads((ROOT/'pass3-routine-life-fix/build-proof.json').read_text())
native_proof=json.loads((ROOT/'pass3-input-clocks/build-proof.json').read_text())
assert w.sha(runner)==proof['runner_sha256']
assert w.sha(harness)==native_proof['harness_binary_sha256']
w.write(OUT/'source-proof.json',{'deadsync':proof,'pack_harness':native_proof})
origins=[
 ROOT/'pass3-routine-life-baselines/routine-life-dance',
 ROOT/'pass3-routine-life-baselines/routine-life-pump',
 ROOT/'pass3-routine-baseline-results/style-dance-routine',
 ROOT/'pass3-routine-baseline-results/style-pump-routine',
 ROOT/'pass3-input-routing-replays/routine-manual-dance',
 ROOT/'pass3-input-routing-replays/routine-manual-pump',
]
for origin in origins:
 old=json.loads((origin/'result.json').read_text())
 assert old['status']=='parity_failure'
 source=next((origin/'candidate').glob('*.tar.zst'))
 assert w.sha(source)==old['candidate_artifact']['sha256']
 case=OUT/old['id'];case.mkdir();candidate=case/(old['candidate_sha256']+'.tar')
 with source.open('rb') as compressed,candidate.open('wb') as decoded:
  zstandard.ZstdDecompressor().copy_stream(compressed,decoded)
 assert w.sha(candidate)==old['candidate_sha256']
 result={'id':old['id'],'source_simfile':old['source_simfile'],'profile':old['profile'],
  'source_snapshot':{'deadsync':proof,'native':old['source_snapshot']},'native':old['native'],
  'capture_reused':True,'candidate_reused':str(source),'baseline_result':str(origin/'result.json'),
  'candidate_sha256':old['candidate_sha256'],'baseline_mismatches':old['comparison']['mismatch_count'],
  'status':'running','started_at':w.now(),'stages':{}}
 w.write(case/'result.json',result)
 result['stages']['replay']=w.execute(case,'replay',[runner,'--archive',candidate,'--report',case/'report.json'],240,memory='6G')
 if (case/'report.json').exists():
  comparison=w.document_summary(case/'report.json',report=True);result['comparison']=comparison
  assert comparison['fixture_sha256']==old['candidate_sha256']
  result['status']='pass' if result['stages']['replay']['exit']==0 and comparison['archive_accepted'] and comparison['mismatch_count']==0 and comparison['error_count']==0 else 'parity_failure'
  if result['status']=='pass':
   result['stages']['pack']=w.execute(case,'pack',[harness,'song-lua-pack',candidate,'--report',case/'report.json','--out',case/'accepted'],180,memory='6G')
   if result['stages']['pack']['exit']:result['status']='packaging_error'
   else:
    packed=next((case/'accepted').glob('*.tar.zst'))
    result['accepted_artifact']={'file':str(packed.relative_to(OUT)),'bytes':packed.stat().st_size,'sha256':w.sha(packed),'uncompressed_sha256':old['candidate_sha256']}
  result['report']=w.compress(case/'report.json',remove=False)
 else:result.update(status='replay_error',reason=(case/'replay.log').read_text(errors='replace')[-8000:])
 result['finished_at']=w.now();w.write(case/'result.json',result)
 print(json.dumps({'id':result['id'],'status':result['status'],'mismatches':result.get('comparison',{}).get('mismatch_count'),'fields':result.get('comparison',{}).get('mismatch_fields'),'errors':result.get('comparison',{}).get('errors')}),flush=True)
