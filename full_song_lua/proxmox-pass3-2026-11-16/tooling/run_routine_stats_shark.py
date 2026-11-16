import json,pathlib,shutil,sys,zstandard
ROOT=pathlib.Path('/opt/song-lua-audit');OUT=ROOT/'pass3-routine-stats-shark-results'
assert not OUT.exists();OUT.mkdir()
sys.path.insert(0,str(ROOT));import worker_pass2 as w
w.RESULTS=OUT
proof=json.loads((ROOT/'pass3-routine-stats-observers-resume/build-proof.json').read_text())
runner=ROOT/'bin/full_song_lua-pass3-routine-stats-observers';assert w.sha(runner)==proof['runner_sha256']
store=ROOT/'routine-stats-shark-inputs';jobs=json.loads((store/'jobs.json').read_text())
w.write(OUT/'source-proof.json',proof)
for job in jobs:
 old=job['baseline'];entry=job['archive'];case=OUT/old['id'];case.mkdir()
 compressed=case/entry['archive']
 with compressed.open('wb') as dst:
  for part in entry['parts']:
   source=store/entry['sha256']/pathlib.Path(part['file']).name
   assert source.stat().st_size==part['bytes'] and w.sha(source)==part['sha256']
   with source.open('rb') as src:shutil.copyfileobj(src,dst,1024*1024)
 assert compressed.stat().st_size==entry['bytes'] and w.sha(compressed)==entry['sha256']
 candidate=case/(old['comparison']['fixture_sha256']+'.tar')
 with compressed.open('rb') as src,candidate.open('wb') as dst:zstandard.ZstdDecompressor().copy_stream(src,dst)
 assert w.sha(candidate)==old['comparison']['fixture_sha256']
 result={'id':old['id'],'source_simfile':old['source_simfile'],'profile':old['profile'],
  'source_snapshot':{'deadsync':proof,'native_baseline':old['source_snapshot']},
  'native':{'harness_version':job['catalog']['harness_version']},'capture_reused':True,
  'published_archive':entry['archive'],'candidate_sha256':old['comparison']['fixture_sha256'],
  'status':'running','started_at':w.now(),'stages':{}}
 w.write(case/'result.json',result)
 result['stages']['replay']=w.execute(case,'replay',[runner,'--archive',candidate,'--report',case/'report.json'],600,memory='6G')
 if (case/'report.json').exists():
  c=w.document_summary(case/'report.json',report=True);result['comparison']=c
  result['status']='pass' if result['stages']['replay']['exit']==0 and c['archive_accepted'] and c['mismatch_count']==0 and c['error_count']==0 else 'parity_failure'
  assert c['fixture_sha256']==old['comparison']['fixture_sha256']
  result['report']=w.compress(case/'report.json',remove=False)
 else:result.update(status='replay_error',reason=(case/'replay.log').read_text(errors='replace')[-8000:])
 result['finished_at']=w.now();w.write(case/'result.json',result)
 print(json.dumps({'id':result['id'],'status':result['status'],'mismatches':result.get('comparison',{}).get('mismatch_count'),'fields':result.get('comparison',{}).get('mismatch_fields')}),flush=True)
