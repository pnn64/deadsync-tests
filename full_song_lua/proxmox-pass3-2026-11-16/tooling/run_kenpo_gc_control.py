"""Distinguish GC-sensitive ordering from ordinary table placement."""
import json,pathlib,sys
ROOT=pathlib.Path('/opt/song-lua-audit');sys.path.insert(0,str(ROOT));import worker_pass2 as w
w.RESULTS=ROOT/'pass3-kenpo-control-results'
assert not w.RESULTS.exists(), 'Do not overwrite or duplicate a diagnostic run'
w.RESULTS.mkdir()
w.RUNNER=ROOT/'bin/full_song_lua-pass3-r2b'
w.HARNESS=ROOT/'bin/itgmania-harness-pass3-r1'
proof=json.loads((ROOT/'pass3-r2b-results/build-proof.json').read_text())
w.write(ROOT/'pass2-source-snapshot.json',{'combined_r2b_build':proof,
    'runner_sha256':w.sha(w.RUNNER),'harness_sha256':w.sha(w.HARNESS),
    'purpose':'GC-stopped diagnostic only; does not replace the automatic-GC primary case'})
job=json.loads((ROOT/'kenpo-gc-control-job.json').read_text())
r=w.run_case(job,'1402')
print(json.dumps({'id':r['id'],'status':r['status'],'mismatches':r.get('comparison',{}).get('mismatch_count')}),flush=True)
