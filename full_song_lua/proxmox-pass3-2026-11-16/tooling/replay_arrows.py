"""Guest 1414: retry retained clean ArrowQuest captures with an 84 GiB cap."""
import json,pathlib,sys
import zstandard
ROOT=pathlib.Path('/opt/song-lua-audit');sys.path.insert(0,str(ROOT));import worker_pass2 as w
w.RESULTS=ROOT/'pass3-arrow-results';w.RESULTS.mkdir(exist_ok=True)
runner=ROOT/'bin/full_song_lua-pass3-profile'
proof=json.loads((ROOT/'pass3-build-proof.json').read_text());assert w.sha(runner)==proof['sha256']
for row in json.loads((ROOT/'arrow-captures/arrow-extraction.json').read_text()):
    case=w.RESULTS/row['id'];case.mkdir(exist_ok=True)
    assert not (case/'result.json').exists(),'Do not replace an existing replay result'
    result={'id':row['id'],'source_simfile':row['source_simfile'],'status':'running','started_at':w.now(),
            'source_snapshot':proof,'capture_reused':row,'vmid':1414,'vm_memory_mib':98304,'memory_limit':'84G'}
    w.write(case/'result.json',result)
    archive=ROOT/'arrow-captures'/pathlib.Path(row['path']).name;assert w.sha(archive)==row['sha256']
    candidate=case/(row['uncompressed_sha256']+'.tar')
    with archive.open('rb') as src,candidate.open('wb') as dst:zstandard.ZstdDecompressor().copy_stream(src,dst)
    assert w.sha(candidate)==row['uncompressed_sha256']
    result['replay']=w.execute(case,'arrow-replay',[runner,'--archive',candidate,'--report',case/'report.json'],10800,memory='84G')
    if (case/'report.json').exists():
        result['comparison']=w.document_summary(case/'report.json',report=True)
        result['status']='pass' if result['replay']['exit']==0 and result['comparison']['archive_accepted'] else 'parity_failure'
        result['report']=w.compress(case/'report.json',remove=True)
    else:
        result['status']=w.failure_category('replay',result['replay'],(case/'arrow-replay.log').read_text(errors='replace'))
    result['finished_at']=w.now();w.write(case/'result.json',result)
    print(json.dumps({'id':row['id'],'status':result['status'],'mismatches':result.get('comparison',{}).get('mismatch_count')}),flush=True)
    assert candidate.resolve().is_relative_to(w.RESULTS.resolve());candidate.unlink()
