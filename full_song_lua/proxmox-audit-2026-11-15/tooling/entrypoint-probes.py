"""Retain native startup logs for cases whose full captures lacked actor definitions."""
import json,pathlib,re,shutil,time,traceback
import worker
root=worker.ROOT;status=root/'results/worker-entrypoint-probes.json'
jobs=json.loads((root/'entrypoint-probe-jobs.json').read_text());done=[]
while not json.loads((root/'results/worker-large.json').read_text()).get('finished_at'):time.sleep(10)
for original in jobs:
 job={**original,'id':'entrypoint-'+original['id'],'primary_id':original['id'],'worker':'large','until_beat':4,'max_events':200000}
 case=root/'results'/job['id'];case.mkdir(exist_ok=True)
 worker.write(status,{'worker':'entrypoint-probes','total':len(jobs),'completed':len(done),'current':job,'updated_at':worker.now()})
 result={'id':job['id'],'primary_id':original['id'],'source_simfile':job['source_simfile'],'title':job['title'],'worker':'large','profile':job,'started_at':worker.now(),'status':'running','stages':{},'artifacts':[]}
 worker.write(case/'result.json',result)
 try:
  sim=root/'Songs'/job['source_simfile'];assert worker.sha(sim)==job['simfile_sha256']
  command=[worker.HARNESS,'song-lua-trace',sim,'--itgmania-bin',worker.ENGINE,'--fallback-theme','Harness Simply Love','--headless','--style',job['style'],'--difficulty',job['difficulty'].removeprefix('Difficulty_'),'--until-beat','4','--capture-fps','60','--max-events','200000','--timeout','120','--keep-run-dir','--out',case/'native.json']
  result['stages']['capture']=worker.execute(case,'capture',command,150,memory='1400M')
  result['native_log_diagnostics']=[]
  for path in (case/'tmp').glob('itgmania-harness-rs/song-lua-*/Logs/log.txt'):
   lines=path.read_text(errors='replace').splitlines();keep=set()
   for index,line in enumerate(lines):
    if re.search(r'error|warning|could not|not found|cannot|does not exist|failed',line,re.I):keep.update(range(max(0,index-1),min(len(lines),index+9)))
   result['native_log_diagnostics'].append({'file':str(path.relative_to(case)),'text':'\n'.join(lines[i] for i in sorted(keep))[:180000]})
  artifact,facts=worker.preserve_diagnostics(case)
  if artifact:result['artifacts'].append(artifact)
  result['native_failure']=facts
  if (case/'native.json').exists():result['artifacts'].append(worker.compress(case/'native.json',remove=True))
  result['status']='native_entrypoint_diagnostic_completed'
 except Exception as error:
  result['status']='entrypoint_diagnostic_error';result['reason']=str(error);result['traceback']=traceback.format_exc()
 finally:
  tmp=case/'tmp'
  if tmp.exists():shutil.rmtree(worker.safe(tmp))
  result['finished_at']=worker.now();worker.write(case/'result.json',result)
 done.append({'id':job['id'],'status':result['status'],'capture_exit':result.get('stages',{}).get('capture',{}).get('exit')})
 print(json.dumps(done[-1]),flush=True)
worker.write(status,{'worker':'entrypoint-probes','total':len(jobs),'completed':len(done),'results':done,'finished_at':worker.now()})
