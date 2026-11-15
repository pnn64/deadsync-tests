import json,os,pathlib,shutil,time,traceback
import zstandard
import worker
ROOT=worker.ROOT
original_execute=worker.execute
def large_execute(*args,**kwargs):
    kwargs['memory']='26G'
    return original_execute(*args,**kwargs)
worker.execute=large_execute
def replay(request):
    job=request['job'];original=request['original'];case=ROOT/'results'/job['id'];case.mkdir(parents=True,exist_ok=True)
    output=case/'result.json'
    result={'id':job['id'],'source_simfile':job['source_simfile'],'title':job['title'],'worker':'large',
            'primary_id':job['primary_id'],'started_at':worker.now(),'profile':job,'status':'running',
            'stages':{},'artifacts':[],'native':original.get('native'),
            'retry_reason':'Replay the same fresh native fixture with a 26 GiB process limit on a 32 GiB VM.',
            'native_capture_worker':original['worker'],'candidate_sha256':original['candidate_sha256']}
    worker.write(output,result)
    raw=case/(original['candidate_sha256']+'.tar')
    try:
        source=ROOT/'retry-inputs'/request['archive']['local_name']
        assert worker.sha(source)==request['archive']['sha256']
        linked=case/(request['archive']['sha256']+'.tar.zst')
        if not linked.exists():os.link(source,linked)
        result['artifacts'].append({'file':str(linked.relative_to(ROOT/'results')),'bytes':linked.stat().st_size,
                                    'sha256':request['archive']['sha256'],'uncompressed_sha256':original['candidate_sha256']})
        with source.open('rb') as packed,raw.open('wb') as target:zstandard.ZstdDecompressor().copy_stream(packed,target)
        assert worker.sha(raw)==original['candidate_sha256']
        result['stages']['replay']=worker.execute(case,'replay',[worker.RUNNER,'--archive',raw,'--report',case/'report.json'],2400)
        if (case/'report.json').exists():
            comparison=worker.document_summary(case/'report.json',report=True);result['comparison']=comparison
            result['status']='pass' if comparison.get('archive_accepted') and result['stages']['replay']['exit']==0 else 'parity_failure'
            if result['status']=='pass':
                command=[worker.HARNESS,'song-lua-pack',raw,'--report',case/'report.json','--out',case/'accepted']
                result['stages']['pack']=worker.execute(case,'pack',command,900)
                if result['stages']['pack']['exit']:result['status']='packaging_error'
                else:
                    packed=next((case/'accepted').glob('*.tar.zst'))
                    result['artifacts'].append({'file':str(packed.relative_to(ROOT/'results')),'bytes':packed.stat().st_size,
                      'sha256':worker.sha(packed),'uncompressed_sha256':original['candidate_sha256']})
            result['artifacts'].append(worker.compress(case/'report.json',remove=True))
        else:
            log=(case/'replay.log').read_text(errors='replace')
            result['status']=worker.failure_category('replay',result['stages']['replay'],log);result['reason']=log[-8000:]
    except Exception as error:result['status']='worker_error';result['reason']=str(error);result['traceback']=traceback.format_exc()
    finally:
        if raw.exists():worker.safe(raw).unlink()
        tmp=case/'tmp'
        if tmp.exists():shutil.rmtree(worker.safe(tmp))
        result['finished_at']=worker.now();worker.write(output,result)
    return result
def main():
    queue=ROOT/'retry-queue';queue.mkdir(exist_ok=True)
    status=ROOT/'results/worker-large.json';done=[]
    while True:
        requests=[json.loads(p.read_text()) for p in queue.glob('*.json')]
        requests.sort(key=lambda r:(r['kind']!='replay',r['job']['id']))
        pending=[r for r in requests if not (ROOT/'results'/r['job']['id']/'result.json').exists()
                 or not json.loads((ROOT/'results'/r['job']['id']/'result.json').read_text()).get('finished_at')]
        worker.write(status,{'worker':'large','total':len(requests),'completed':len(requests)-len(pending),
                            'current':pending[0]['job'] if pending else None,'updated_at':worker.now()})
        if not pending:
            if (ROOT/'retry-queue.closed').exists():break
            time.sleep(10);continue
        request=pending[0]
        result=replay(request) if request['kind']=='replay' else worker.run_case(request['job'],'large')
        print(json.dumps({'id':result['id'],'primary_id':request['job']['primary_id'],'status':result['status']}),flush=True)
    worker.write(status,{'worker':'large','total':len(requests),'completed':len(requests),'finished_at':worker.now()})
if __name__=='__main__':main()
