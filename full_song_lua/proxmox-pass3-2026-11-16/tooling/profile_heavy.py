"""Guest: collect two full samply replays for each of three heavy fixtures."""
import datetime,gzip,hashlib,json,pathlib,shutil,subprocess,sys,time,traceback
import zstandard
ROOT=pathlib.Path('/opt/song-lua-audit');sys.path.insert(0,str(ROOT))
import worker_pass2 as w
OUT=ROOT/'pass3-profiles';OUT.mkdir(exist_ok=True);w.RESULTS=OUT
RUNNER=ROOT/'bin/full_song_lua-pass3-profile';SAMPLY=ROOT/'profiler/samply'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,obj):
    temp=p.with_suffix('.tmp');temp.write_text(json.dumps(obj,indent=2)+'\n');temp.replace(p)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
proof=json.loads((ROOT/'pass3-build-proof.json').read_text());assert sha(RUNNER)==proof['sha256']
save(OUT/'build-proof.json',proof)
shutil.copy2(ROOT/'profiler/installation.json',OUT/'samply-installation.json')
rows={r['id']:r for r in json.loads((ROOT/'retained-captures/retained-extraction.json').read_text())}
jobs=[('9a7dc9dd696c05ad','mr-sandman'),('6a3e1a6f93bdc9fc','paint-ssc'),('e115c0f3019c18b4','fof')]
old=subprocess.check_output(['sysctl','-n','kernel.perf_event_paranoid'],text=True).strip()
save(OUT/'perf-permissions.json',{'original_perf_event_paranoid':old,'temporary_value':-1,'scope':'dedicated guest only'})
subprocess.run(['sudo','sysctl','-w','kernel.perf_event_paranoid=-1'],check=True)
try:
    # Verify the profiler can sample this guest before spending time on a song.
    smoke=OUT/'samply-smoke.json.gz'
    subprocess.run([str(SAMPLY),'record','--save-only','--rate','99','--output',str(smoke),'--',
                    '/usr/bin/python3','-c','import time; end=time.monotonic()+2\nwhile time.monotonic()<end: pass'],check=True)
    with gzip.open(smoke,'rt') as f:smoke_data=json.load(f)
    assert sum(t.get('samples',{}).get('length',0) for t in smoke_data['threads'])>20
    for ident,label in jobs:
        row=rows[ident];case=OUT/label;case.mkdir(exist_ok=True)
        archive=ROOT/'retained-captures'/pathlib.Path(row['path']).name;assert sha(archive)==row['sha256']
        candidate=case/(row['uncompressed_sha256']+'.tar')
        with archive.open('rb') as src,candidate.open('wb') as dst:zstandard.ZstdDecompressor().copy_stream(src,dst)
        assert sha(candidate)==row['uncompressed_sha256']
        for iteration in [1,2]:
            run_dir=case/f'run-{iteration}';run_dir.mkdir(exist_ok=True)
            assert not (run_dir/'result.json').exists(),'Never overwrite an existing profile run'
            profile=run_dir/'profile.json.gz';report=run_dir/'report.json'
            argv=[str(SAMPLY),'record','--save-only','--unstable-presymbolicate','--rate','99',
                  '--profile-name',f'{label} baseline pass3 run {iteration}','--output',str(profile),
                  '--',str(RUNNER),'--archive',str(candidate),'--report',str(report)]
            result={'id':ident,'song':row['source_simfile'],'iteration':iteration,'started_at':now(),
                    'runner_sha256':proof['sha256'],'capture':row,'sample_rate_hz':99,
                    'cache_policy':'OS caches uncontrolled; sequential repeated runs',
                    'vm_cpus':2,'vm_memory_mib':65536,'status':'running'}
            save(run_dir/'result.json',result)
            print('Starting profile',label,iteration,flush=True)
            result['execution']=w.execute(run_dir,'profile',argv,7200,memory='58G')
            if report.exists():
                result['comparison']=w.document_summary(report,report=True)
                result['report']=w.compress(report,remove=True)
            if profile.exists():
                with gzip.open(profile,'rt') as f:data=json.load(f)
                result['samples']=sum(t.get('samples',{}).get('length',0) for t in data['threads'])
                result['threads']=[{'name':t['name'],'samples':t.get('samples',{}).get('length',0)} for t in data['threads']]
                del data
                result['artifacts']=[{'path':str(p.relative_to(OUT)),'bytes':p.stat().st_size,'sha256':sha(p)}
                    for p in run_dir.glob('profile*') if p.is_file() and p.suffix in ['.gz','.json']]
                result['symbols_saved']=any('syms' in a['path'] for a in result['artifacts'])
            result['status']='complete' if result['execution']['exit']==0 and result.get('samples',0)>100 and result.get('symbols_saved') else 'profile_failed'
            result['parity_pass']=result.get('comparison',{}).get('archive_accepted')==True
            result['finished_at']=now();save(run_dir/'result.json',result)
            print('Finished profile',label,iteration,result['status'],'parity',result['parity_pass'],flush=True)
            assert result['status']=='complete',result
        assert candidate.resolve().is_relative_to(OUT.resolve());candidate.unlink()
    save(OUT/'complete.json',{'finished_at':now(),'runs':6,'fixtures':3})
except BaseException:
    save(OUT/'error.json',{'at':now(),'traceback':traceback.format_exc()});raise
finally:
    subprocess.run(['sudo','sysctl','-w','kernel.perf_event_paranoid='+old],check=True)
