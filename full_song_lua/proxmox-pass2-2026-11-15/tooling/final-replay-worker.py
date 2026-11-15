import hashlib,json,pathlib,sys,time,traceback,shutil
import zstandard
ROOT=pathlib.Path('/opt/song-lua-audit');sys.path.insert(0,str(ROOT))
import worker_pass2 as w
w.RESULTS=ROOT/'pass2-final-results';w.RESULTS.mkdir(exist_ok=True)
w.RUNNER=ROOT/'bin/full_song_lua-final-validation'
proof=json.loads((ROOT/'final-validation-source-snapshot.json').read_text())
binary_sha=w.sha(w.RUNNER)
jobs=json.loads(pathlib.Path(sys.argv[1]).read_text())
for job in jobs:
 case=w.RESULTS/job['id'];case.mkdir(exist_ok=True)
 if (case/'result.json').exists():
  prior=json.loads((case/'result.json').read_text())
  if prior.get('finished_at'):
   if prior.get('status')=='replay_error' and 'archive content address' in prior.get('reason',''):
    (case/'result.json').rename(case/'result-before-address-retry.json')
   else:continue
 result={**job,'status':'running','started_at':w.now(),'stages':{},'artifacts':[],
         'source_snapshot':proof,'runner_sha256':binary_sha,'native_capture_reused':True,
         'capture_result_directory':job.get('result_directory','pass2-results'),
         'capture_source_snapshot':job['source_snapshot']}
 result.pop('comparison',None);result.pop('reason',None);result.pop('finished_at',None)
 w.write(case/'result.json',result)
 candidate=None
 try:
  w.STAGE_MEMORY=job.get('final_memory','6G')
  artifacts=job['artifacts']
  a=next((a for a in artifacts if '/accepted/' in a['file']),None)
  if not a:a=next(a for a in artifacts if '/candidate/' in a['file'] and a['file'].endswith('.tar.zst'))
  source=ROOT/job.get('result_directory','pass2-results')/a['file']
  candidate=case/(a['uncompressed_sha256']+'.tar')
  assert w.sha(source)==a['sha256']
  with source.open('rb') as src,candidate.open('wb') as dst:zstandard.ZstdDecompressor().copy_stream(src,dst)
  assert w.sha(candidate)==a['uncompressed_sha256']
  result['candidate_sha256']=a['uncompressed_sha256']
  result['capture_archive']={'path':str(source),'sha256':a['sha256'],'uncompressed_sha256':a['uncompressed_sha256']}
  result['stages']['replay']=w.execute(case,'final-replay',[w.RUNNER,'--archive',candidate,'--report',case/'report.json'],job.get('final_timeout',3600))
  if (case/'report.json').exists():
   summary=w.document_summary(case/'report.json',report=True);result['comparison']=summary
   result['status']='pass' if summary['archive_accepted'] and not result['stages']['replay']['exit'] else 'parity_failure'
   if result['status']=='pass':
    result['stages']['pack']=w.execute(case,'final-pack',[w.HARNESS,'song-lua-pack',candidate,'--report',case/'report.json','--out',case/'accepted'],900)
    assert result['stages']['pack']['exit']==0
    packed=next((case/'accepted').glob('*.tar.zst'))
    result['artifacts'].append(dict(file=str(packed.relative_to(w.RESULTS)),bytes=packed.stat().st_size,sha256=w.sha(packed),uncompressed_sha256=a['uncompressed_sha256']))
   result['artifacts'].append(w.compress(case/'report.json',remove=True))
  else:
   log=(case/'final-replay.log').read_text(errors='replace')
   result['status']=w.failure_category('replay',result['stages']['replay'],log);result['reason']=log[-8000:]
 except Exception as error:
  result['status']='worker_error';result['reason']=str(error);result['traceback']=traceback.format_exc()
 finally:
  if candidate is not None and candidate.exists():w.safe(candidate).unlink()
  result['finished_at']=w.now();w.write(case/'result.json',result)
 print(json.dumps({'id':job['id'],'status':result['status'],'mismatches':result.get('comparison',{}).get('mismatch_count')}),flush=True)
