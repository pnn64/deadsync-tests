"""Read-only final check for orphan native/capture/replay processes."""
import concurrent.futures,datetime,json
from remote import WORK,run
fleet=json.loads((WORK/'fleet.json').read_text())+[json.loads((WORK/'retry-vm.json').read_text())]
probe="""import datetime,json,pathlib,subprocess
root=pathlib.Path('/opt/song-lua-audit');processes=[]
for p in pathlib.Path('/proc').glob('[0-9]*/cmdline'):
 try:
  args=[s.decode(errors='replace') for s in p.read_bytes().split(b'\\0') if s]
  if not args:continue
  task=any(a.startswith(str(root)+'/') for a in args)
  program=pathlib.Path(args[0]).name
  if task and (program in ['ITGmania-harness-trace','itgmania-harness-rs','full_song_lua','valgrind'] or any(a.endswith('/'+n) for a in args for n in ['worker.py','large-worker.py','capture-pool.py','pool-retry.py','recheck-video.py','bank-versus-control.py','entrypoint-probes.py','coverage-controls.py'])):
   processes.append({'pid':p.parent.name,'args':args,'status':(p.parent/'status').read_text().splitlines()[:7]})
 except (FileNotFoundError,PermissionError,ProcessLookupError):pass
statuses=[json.loads(p.read_text()) for p in (root/'results').glob('worker-*.json')]
sources={}
for folder,expected in [('deadsync','959b8b04d5078be603478e4459938ac37f9e39fd'),('harness','00f50340b5edda2a54dcdf78e38d4f9079a561da'),('harness/vendor/itgmania','5c737928d93778c2c9f68e276052b220b43a468f'),('harness/vendor/simply-love','dd06138b15492f4136796dfe4b6708ced0f7b9eb')]:
 revision=subprocess.check_output(['git','-C',str(root/folder),'rev-parse','HEAD'],text=True).strip()
 changes=subprocess.check_output(['git','-C',str(root/folder),'status','--porcelain=v1','--untracked-files=no'],text=True).strip()
 sources[folder]={'revision':revision,'expected':expected,'tracked_changes':changes,'valid':revision==expected and not changes}
print(json.dumps({'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'processes':processes,'unfinished_workers':[s for s in statuses if not s.get('finished_at')],'sources':sources}))
"""
def check(w):
 data=json.loads(run(probe,ip=w['ip'],capture_output=True,timeout=30).stdout)
 return {'worker':w['worker'],'ip':w['ip'],**data}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:results=list(pool.map(check,fleet))
data={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'complete':len(results)==16 and all(not w['processes'] and not w['unfinished_workers'] and all(s['valid'] for s in w['sources'].values()) for w in results),'workers':results}
(WORK/'process-verification.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'complete':data['complete'],
 'active':[{'worker':w['worker'],'pids':[p['pid'] for p in w['processes']],'unfinished':[s['worker'] for s in w['unfinished_workers']]} for w in results if w['processes'] or w['unfinished_workers']],
 'source_failures':[{'worker':w['worker'],'source':name,**s} for w in results for name,s in w['sources'].items() if not s['valid']]}))
