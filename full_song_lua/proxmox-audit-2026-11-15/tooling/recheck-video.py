import argparse,datetime,json,pathlib,shutil,subprocess,time,traceback
import zstandard
import worker
root=worker.ROOT
def recheck(case):
    destination=case/'video-recheck.json'
    if destination.exists():return json.loads(destination.read_text())
    original=json.loads((case/'result.json').read_text())
    if 'replay' not in original.get('stages',{}):return None
    receipt=json.loads((root/'video-tools-provenance.json').read_text())
    if original['started_at']>receipt['installed_at']:return None
    scratch=case/'rechecks'/('video-tools-'+case.name);scratch.mkdir(parents=True,exist_ok=True)
    result={'reason':'Replayed the same fresh native fixture after installing missing ffprobe/ffmpeg tools.',
            'started_at':worker.now(),'dependency_receipt':receipt,'stages':{},'artifacts':[]}
    try:
        archives=[root/'results'/a['file'] for a in original['artifacts'] if a['file'].endswith('.tar.zst') and 'native-diagnostics' not in a['file']]
        assert len(archives)==1,archives
        archive=archives[0]
        result['source_archive']=str(archive.relative_to(root/'results'))
        result['source_archive_sha256']=worker.sha(archive)
        raw=scratch/(original['candidate_sha256']+'.tar')
        with archive.open('rb') as source,raw.open('wb') as target:zstandard.ZstdDecompressor().copy_stream(source,target)
        assert worker.sha(raw)==original['candidate_sha256']
        command=[worker.RUNNER,'--archive',raw,'--report',scratch/'report.json']
        result['stages']['replay']=worker.execute(scratch,'replay',command,1200)
        if not (scratch/'report.json').exists():
            result['status']='replay_error';result['reason']+=(scratch/'replay.log').read_text(errors='replace')[-5000:]
        else:
            comparison=worker.document_summary(scratch/'report.json',report=True);result['comparison']=comparison
            result['status']='pass' if comparison.get('archive_accepted') and result['stages']['replay']['exit']==0 else 'parity_failure'
            if result['status']=='pass' and original['status']!='pass':
                command=[worker.HARNESS,'song-lua-pack',raw,'--report',scratch/'report.json','--out',scratch/'accepted']
                result['stages']['pack']=worker.execute(scratch,'pack',command,600)
                if result['stages']['pack']['exit']:result['status']='packaging_error'
                else:
                    packed=next((scratch/'accepted').glob('*.tar.zst'))
                    result['artifacts'].append({'file':str(packed.relative_to(root/'results')),'sha256':worker.sha(packed),
                                               'bytes':packed.stat().st_size,'uncompressed_sha256':original['candidate_sha256']})
                    worker.safe(raw).unlink()
            result['artifacts'].append(worker.compress(scratch/'report.json',remove=True))
        if raw.exists():worker.safe(raw).unlink()
    except Exception as error:result['status']='recheck_error';result['error']=str(error);result['traceback']=traceback.format_exc()
    result['finished_at']=worker.now();worker.write(destination,result)
    print(json.dumps({'id':case.name,'status':result['status']}),flush=True)
    return result
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--worker',required=True);parser.add_argument('--case')
    args=parser.parse_args()
    if args.case:recheck(root/'results'/args.case);return
    status=root/'results'/('video-recheck-'+args.worker+'.json')
    worker.write(status,{'status':'waiting_for_primary','worker':args.worker})
    while subprocess.run(['systemctl','is-active','--quiet','song-lua-audit-'+args.worker]).returncode==0:time.sleep(15)
    jobs=json.loads((root/'shards'/(args.worker+'.json')).read_text())
    results=[]
    for job in jobs:
        case=root/'results'/job['id']
        if (case/'result.json').exists():
            result=recheck(case)
            if result:results.append({'id':job['id'],'status':result['status']})
    worker.write(status,{'status':'finished','worker':args.worker,'results':results,'finished_at':worker.now()})
if __name__=='__main__':main()
