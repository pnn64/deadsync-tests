#!/usr/bin/env python3
"""Run fresh native captures and patched DeadSync comparisons, one case at a time."""
import argparse, collections, datetime, hashlib, json, os, pathlib, shutil
import subprocess, tarfile, time, traceback
import ijson
from ijson.common import ObjectBuilder
import zstandard

ROOT=pathlib.Path('/opt/song-lua-audit')
RESULTS=ROOT/'pass2-results'
STAGE_MEMORY='6G'
HARNESS=ROOT/'bin/itgmania-harness-rs'
RUNNER=ROOT/'bin/full_song_lua'
ENGINE=ROOT/'harness/vendor/itgmania/ITGmania-harness-trace'
THEME=ENGINE.parent/'Themes/Harness Simply Love'
NATIVE_REVISION='008bfcfef57a107eaafe08b4de7d9d42c6dd1e2f'

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(path,value):
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    temp.replace(path)
def safe(path):
    path=path.resolve()
    assert path.is_relative_to(RESULTS) and path!=RESULTS
    return path
def bounded(value,depth=0):
    if depth>7:return '<nested value omitted; see full report>'
    if isinstance(value,str):return value[:1800]
    if isinstance(value,list):return [bounded(v,depth+1) for v in value[:24]]
    if isinstance(value,dict):return {k:bounded(v,depth+1) for k,v in list(value.items())[:35]}
    return value

def document_summary(path,report=False):
    fields={'schema_version','harness_version','command_observer','completion','input',
            'script_errors','transition_script_errors','capture_limits','style','difficulty','steps_type','end_position','error'}
    if report:fields={'archive_accepted','fixture_sha256','native_frames','replayed_frames',
                     'compared_stage_fields','execution_path','whole_song_parity_proven',
                     'pending_coverage','capture_completed_gameplay','production_preparation_exercised',
                     'production_parity_proven','acceptance_basis'}
    result={};active=None;builder=None;depth=0;mismatches=0;groups=collections.Counter();samples=[]
    error_count=0;errors=[]
    with path.open('rb') as stream:
        for prefix,event,value in ijson.parse(stream,use_float=True):
            if active is not None:
                builder.event(event,value)
                if event in ('start_map','start_array'):depth+=1
                elif event in ('end_map','end_array'):depth-=1
                if depth==0:
                    if active=='mismatches.item':samples.append(bounded(builder.value))
                    elif active=='errors.item':errors.append(bounded(builder.value))
                    else:result[active]=builder.value
                    active=None;builder=None
                continue
            if report and prefix=='errors.item' and event not in ('end_map','end_array','map_key'):
                error_count+=1
                if event in ('start_map','start_array') and len(errors)<40:
                    active=prefix;builder=ObjectBuilder();builder.event(event,value);depth=1
                elif event not in ('start_map','start_array') and len(errors)<40:errors.append(bounded(value))
                continue
            if report and prefix=='mismatches.item.field' and event=='string':groups[value]+=1
            if report and prefix=='mismatches.item' and event=='start_map':
                mismatches+=1
                if len(samples)<40:
                    active=prefix;builder=ObjectBuilder();builder.event(event,value);depth=1
                continue
            if prefix in fields or ('.' not in prefix and prefix.startswith('dropped_')):
                if event in ('start_map','start_array'):
                    active=prefix;builder=ObjectBuilder();builder.event(event,value);depth=1
                elif event not in ('map_key','end_map','end_array'):result[prefix]=value
    if report:
        for sample in samples:groups[sample.get('field','unknown')]+=1
        result.update(mismatch_count=mismatches,mismatch_fields=dict(groups),first_mismatches=samples,
                      error_count=error_count,errors=errors)
    return result

def native_errors(path):
    errors=[]
    try:
        with path.open('rb') as f:
            for item in ijson.items(f,'events.item',use_float=True):
                if item.get('kind')=='error':errors.append(bounded(item))
                if len(errors)>=30:break
    except Exception as error:errors.append({'incomplete_json':str(error)})
    return errors

def execute(case,stage,command,limit,memory=None):
    memory=memory or STAGE_MEMORY
    unit='lua-pass2-'+case.name+'-'+stage
    tmp=case/'tmp';tmp.mkdir(exist_ok=True)
    argv=['sudo','systemd-run','--quiet','--wait','--pipe','--collect',
          '--unit='+unit,'--property=MemoryMax='+memory,'--property=MemorySwapMax=0',
          '--property=OOMPolicy=kill','--property=RuntimeMaxSec='+str(limit),
          '--property=User=parity','--property=Group=parity',
          '--working-directory='+str(ROOT),
          '--setenv=TMPDIR='+str(tmp),
          '--setenv=ITGMANIA_SONG_LUA_NOTESKIN_ROOT='+str(ROOT/'deadsync/assets/noteskins'),
          *map(str,command)]
    started=time.monotonic()
    with (case/(stage+'.log')).open('w') as log:
        code=subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT).returncode
    journal=subprocess.run(['sudo','journalctl','--no-pager','-u',unit,'-o','short-iso','-n','24'],capture_output=True,text=True)
    (case/(stage+'-service.log')).write_text(journal.stdout+journal.stderr)
    return {'command':list(map(str,command)),'exit':code,'elapsed_seconds':round(time.monotonic()-started,3),
            'memory_limit':memory,'timeout_seconds':limit,'unit':unit,
            'service_tail':(journal.stdout+journal.stderr)[-5000:]}

def compress(path,remove=False):
    target=path.with_suffix(path.suffix+'.zst');original=sha(path)
    with path.open('rb') as source,target.open('wb') as dest:
        zstandard.ZstdCompressor(level=3,write_checksum=True).copy_stream(source,dest)
    digest=hashlib.sha256()
    with target.open('rb') as source,zstandard.ZstdDecompressor().stream_reader(source) as decoded:
        while block:=decoded.read(4*1024*1024):digest.update(block)
    assert digest.hexdigest()==original,'compressed artifact failed round-trip verification'
    record={'file':str(target.relative_to(RESULTS)),'bytes':target.stat().st_size,
            'sha256':sha(target),'uncompressed_sha256':original}
    if remove:safe(path).unlink()
    return record

def preserve_diagnostics(case):
    diagnostics=case/'native-diagnostics';diagnostics.mkdir(exist_ok=True)
    for install in sorted((case/'tmp/itgmania-harness-rs').glob('song-lua-*')):
        dest=diagnostics/install.name;dest.mkdir(exist_ok=True)
        for name in ['Logs','Save/itgmania-harness','Save/Preferences.ini','crashinfo.txt']:
            path=install/name
            if path.is_dir():shutil.copytree(path,dest/name,dirs_exist_ok=True)
            elif path.is_file():
                (dest/name).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest/name)
    raw=list(diagnostics.glob('*/Save/itgmania-harness/song-lua-trace.json'))
    facts=[]
    for path in raw:
        try:facts.append({'summary':document_summary(path),'errors':native_errors(path)})
        except Exception as error:facts.append({'parse_error':str(error)})
    write(case/'native-failure-details.json',facts)
    if any(diagnostics.rglob('*')):
        archive=case/'native-diagnostics.tar'
        with tarfile.open(archive,'w') as tar:tar.add(diagnostics,arcname='native-diagnostics')
        artifact=compress(archive,remove=True)
        shutil.rmtree(safe(diagnostics))
        return artifact,facts
    return None,facts

def failure_category(stage,result,log):
    text=(log+' '+result.get('service_tail','')).lower()
    if 'oom-kill' in text or 'out of memory' in text or 'memory allocation' in text:return stage+'_resource_limit'
    if ('timed out' in log.lower() or 'did not write a semantic trace within ' in log.lower()
        or "result 'timeout'" in text or 'runtime limit exceeded' in text):return stage+'_timeout'
    if stage=='capture':
        if 'native script loading or execution failed' in text:return 'native_lua_error'
        if 'no stepstype_' in text or 'loaded no charts' in text:return 'no_selectable_chart'
        if 'cannot open' in text or 'no such file' in text:return 'native_missing_input'
        if 'crash' in text:return 'native_crash'
        if 'exited with' in log.lower():return 'native_process_exit'
        return 'native_capture_error'
    return stage+'_error'

def run_case(job,worker):
    global STAGE_MEMORY
    STAGE_MEMORY=job.get('stage_memory','6G')
    case=RESULTS/job['id'];case.mkdir(parents=True,exist_ok=True)
    destination=case/'result.json'
    if destination.exists() and json.loads(destination.read_text()).get('finished_at'):
        return json.loads(destination.read_text())
    result={'id':job['id'],'source_simfile':job['source_simfile'],'title':job.get('title'),
            'worker':worker,'started_at':now(),'profile':job,'source_snapshot':json.loads((ROOT/'pass2-source-snapshot.json').read_text()),'status':'running','stages':{},'artifacts':[]}
    write(destination,result)
    try:
        assert shutil.disk_usage(ROOT).free>6*1024**3,'less than 6 GiB free on worker'
        simfile=ROOT/'Songs'/job['source_simfile']
        assert sha(simfile)==job['simfile_sha256'],'simfile differs from frozen corpus'
        trace=case/'traces';trace.mkdir(exist_ok=True)
        command=[HARNESS,'song-lua-trace',simfile,'--itgmania-bin',ENGINE,
                 '--fallback-theme','Harness Simply Love','--headless','--style',job['style'],
                 '--until-gameplay-end','--capture-fps',str(job.get('capture_fps',60)),
                 '--max-events',str(job.get('max_events',2000000)),
                 '--timeout',str(job.get('capture_timeout',900)),'--out',trace/'native.json']
        if job.get('difficulty'):command+=['--difficulty',job['difficulty'].removeprefix('Difficulty_')]
        if job.get('fixed_update_fps'):command+=['--fixed-update-fps',str(job['fixed_update_fps'])]
        if job.get('gc_mode')=='stopped':command+=['--stop-lua-gc']
        result['stages']['capture']=execute(case,'capture',command,job.get('capture_timeout',900)+90)
        if result['stages']['capture']['exit']:
            log=(case/'capture.log').read_text(errors='replace')
            result['status']=failure_category('capture',result['stages']['capture'],log)
            result['reason']=log[-8000:]
            artifact,facts=preserve_diagnostics(case)
            if artifact:result['artifacts'].append(artifact)
            result['native_failure']=facts
            return result
        native=document_summary(trace/'native.json')
        source=native['input']['native_source']
        assert source['revision']==NATIVE_REVISION and source['modified_src'] is False
        assert native['completion']['reason']=='gameplay-exit'
        result['native']=native
        wrapper={'fixture_schema_version':1,'oracle_schema_version':native['schema_version'],
                 'harness_version':native['harness_version'],
                 'itgmania':{'git_revision':source['revision'],'git_dirty':'false'},
                 'simfiles':[{'simfile':job['source_simfile'],'fixture':'native.json',
                              'title':job.get('title',job['source_simfile']),'status':'ok',
                              'command_observer':native['command_observer']}]}
        write(trace/'_semantic_manifest.json',wrapper)
        command=[HARNESS,'song-lua-archive',ROOT/'Songs','--traces',trace,'--out',case/'candidate',
                 '--uncompressed','--theme-assets',THEME]
        result['stages']['archive']=execute(case,'archive',command,600)
        if result['stages']['archive']['exit']:
            result['status']=failure_category('archive',result['stages']['archive'],(case/'archive.log').read_text(errors='replace'))
            result['reason']=(case/'archive.log').read_text(errors='replace')[-8000:]
            return result
        entry=json.loads((case/'candidate/index.json').read_bytes())['archives'][0]
        candidate=case/'candidate'/entry['archive']
        result['candidate_sha256']=sha(candidate)
        command=[RUNNER,'--archive',candidate,'--report',case/'report.json']
        result['stages']['replay']=execute(case,'replay',command,job.get('replay_timeout',1200))
        if (case/'report.json').exists():
            report=document_summary(case/'report.json',report=True);result['comparison']=report
            if report.get('archive_accepted') and not result['stages']['replay']['exit']:
                result['status']='pass'
                command=[HARNESS,'song-lua-pack',candidate,'--report',case/'report.json','--out',case/'accepted']
                result['stages']['pack']=execute(case,'pack',command,600)
                if result['stages']['pack']['exit']:
                    result['status']='packaging_error'
                else:
                    packed=next((case/'accepted').glob('*.tar.zst'))
                    result['artifacts'].append({'file':str(packed.relative_to(RESULTS)),
                        'bytes':packed.stat().st_size,'sha256':sha(packed),'uncompressed_sha256':result['candidate_sha256']})
                    safe(candidate).unlink()
            else:result['status']='parity_failure'
            result['artifacts'].append(compress(case/'report.json',remove=True))
        else:
            log=(case/'replay.log').read_text(errors='replace')
            result['status']=failure_category('replay',result['stages']['replay'],log)
            result['reason']=log[-8000:]
        if candidate.exists():result['artifacts'].append(compress(candidate,remove=True))
        # The verified candidate contains the native trace and all captured assets.
        safe(trace/'native.json').unlink()
        return result
    except Exception as error:
        result['status']='worker_error';result['reason']=str(error);result['traceback']=traceback.format_exc()
        return result
    finally:
        # Retain any sole remaining trace when packaging was unsuccessful.
        trace=case/'traces/native.json'
        if trace.exists():
            try:result['artifacts'].append(compress(trace,remove=True))
            except Exception as error:result['retention_error']=str(error)
        scratch=case/'tmp'
        if scratch.exists():shutil.rmtree(safe(scratch))
        result['finished_at']=now();write(destination,result)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('manifest');parser.add_argument('--worker',required=True)
    args=parser.parse_args();jobs=json.loads(pathlib.Path(args.manifest).read_text())
    status=RESULTS/('worker-'+args.worker+'.json');status.parent.mkdir(exist_ok=True)
    done=[]
    for job in jobs:
        write(status,{'worker':args.worker,'total':len(jobs),'completed':len(done),'current':job,'updated_at':now()})
        result=run_case(job,args.worker);done.append({'id':job['id'],'source_simfile':job['source_simfile'],'status':result['status']})
        print(json.dumps(done[-1]),flush=True)
    write(status,{'worker':args.worker,'total':len(jobs),'completed':len(done),'results':done,'finished_at':now()})
if __name__=='__main__':main()

