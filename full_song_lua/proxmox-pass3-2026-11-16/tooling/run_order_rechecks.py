"""Fresh KENPO captures distinguish repeatable semantic gaps from native ordering."""
import json,pathlib,sys
ROOT=pathlib.Path('/opt/song-lua-audit')
sys.path.insert(0,str(ROOT));import worker_pass2 as w
w.RESULTS=ROOT/'pass3-order-results';w.RESULTS.mkdir(exist_ok=True)
w.HARNESS=ROOT/'bin/itgmania-harness-pass3-r1'
w.RUNNER=ROOT/'bin/full_song_lua-pass3-r1b'
for job in json.loads((ROOT/'order-jobs.json').read_text()):
    result=w.run_case(job,'1401')
    print(json.dumps({'id':job['id'],'status':result['status'],'mismatches':result.get('comparison',{}).get('mismatch_count')}),flush=True)
