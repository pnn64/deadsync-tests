"""Read-only post-run verification on one guest; never repairs corpus or artifacts."""
import datetime,hashlib,json,pathlib,subprocess
ROOT=pathlib.Path('/opt/song-lua-audit')
def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
manifest=json.loads((ROOT/'inputs/corpus-manifest.json').read_text())
failures=[];total_bytes=0
for entry in manifest:
    path=ROOT/'Songs'/entry['path']
    if not path.is_file():failures.append({'kind':'missing_input','path':entry['path']});continue
    total_bytes+=path.stat().st_size
    if path.stat().st_size!=entry['bytes'] or sha(path)!=entry['sha256']:
        failures.append({'kind':'changed_input','path':entry['path'],'expected':entry['sha256'],'actual':sha(path)})
expected_paths={e['path'] for e in manifest}
extra=[p.relative_to(ROOT/'Songs').as_posix() for p in (ROOT/'Songs').rglob('*') if p.is_file() and p.relative_to(ROOT/'Songs').as_posix() not in expected_paths]
artifacts={};unfinished=[]
for path in (ROOT/'results').glob('*/result.json'):
    r=json.loads(path.read_text())
    if not r.get('finished_at'):unfinished.append(r['id']);continue
    records=r.get('artifacts',[])
    recheck=path.parent/'video-recheck.json'
    if recheck.exists():records+=json.loads(recheck.read_text()).get('artifacts',[])
    for entry in records:
        target=(ROOT/'results'/entry['file']).resolve()
        assert target.is_relative_to(ROOT/'results')
        if str(target) in artifacts:continue
        if not target.is_file():failures.append({'kind':'missing_artifact','file':entry['file']});continue
        digest=sha(target)
        artifacts[str(target)]={'sha256':digest,'bytes':target.stat().st_size}
        if digest!=entry['sha256'] or target.stat().st_size!=entry['bytes']:
            failures.append({'kind':'changed_artifact','file':entry['file'],'actual':digest,'expected':entry['sha256']})
binaries={name:sha(ROOT/name) for name in ['bin/full_song_lua','bin/itgmania-harness-rs','harness/vendor/itgmania/ITGmania-harness-trace']}
result={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'corpus_files':len(manifest),
        'corpus_bytes':total_bytes,'extra_corpus_files':extra,'artifacts_checked':len(artifacts),
        'artifact_bytes':sum(a['bytes'] for a in artifacts.values()),'binaries':binaries,'unfinished_results':unfinished,'failures':failures}
print(json.dumps(result))
