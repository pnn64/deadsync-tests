"""Retry one truncated native capture with an explicit, larger event budget."""
import json,pathlib,shutil,sys
ROOT=pathlib.Path('/opt/song-lua-audit');sys.path.insert(0,str(ROOT));import worker_pass2 as w
w.RESULTS=ROOT/'pass3-james-budget-results'
assert not w.RESULTS.exists(), 'Existing attempts must be observed, not restarted'
assert shutil.disk_usage(ROOT).free>100*1024**3
w.RESULTS.mkdir()
w.RUNNER=ROOT/'bin/full_song_lua-pass3-gc';w.HARNESS=ROOT/'bin/itgmania-harness-pass3-r1'
proof=json.loads((ROOT/'pass3-gc-build-proof.json').read_text())
harness=json.loads((ROOT/'pass3-r1-proof-from-1401.json').read_text())
assert w.sha(w.RUNNER)==proof['runner_sha256']
assert w.sha(w.HARNESS)==harness['binaries']['itgmania-harness-pass3-r1']
w.write(ROOT/'pass2-source-snapshot.json',{'deadsync':proof,'harness':harness,
    'resource_setup':json.loads((ROOT/'james-resource-setup.json').read_text())})
execute=w.execute
def bounded(case,stage,command,limit,memory=None):
    # Large completed traces need time for archive verification and packing too.
    if stage in ['archive','pack']:limit=1800
    return execute(case,stage,command,limit,memory)
w.execute=bounded
job=json.loads((ROOT/'james-budget-job.json').read_text())
r=w.run_case(job,'1414')
print(json.dumps({'id':r['id'],'status':r['status'],'mismatches':r.get('comparison',{}).get('mismatch_count')}),flush=True)
