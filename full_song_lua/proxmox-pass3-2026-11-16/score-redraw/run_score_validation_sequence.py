import datetime,json,pathlib,subprocess,time
root=pathlib.Path('/opt/song-lua-audit');out=root/'pass3-score-validation-sequence.json'
assert not out.exists()
state={'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'waiting_for_builds','steps':[]}
def save():out.write_text(json.dumps(state,indent=2)+'\n')
save()
for suffix in ['score-redraw-build-final','score-harness-final']:
 unit='song-lua-pass3-'+suffix
 while True:
  props=dict(line.split('=',1) for line in subprocess.check_output(['systemctl','show',unit,'-p','LoadState','-p','ActiveState','-p','ExecMainStatus'],text=True).splitlines())
  assert props['LoadState']=='loaded',props
  if props['ActiveState'] not in ['active','activating','deactivating']:break
  time.sleep(5)
 assert props['ExecMainStatus']=='0' and props['ActiveState']=='inactive',props
 assert (root/('pass3-'+suffix)/'build-proof.json').exists(),suffix
state['status']='running';save()
for name in ['run_score_final_controls.py','run_score_regressions.py']:
 with (root/'logs'/name.replace('.py','.log')).open('w') as log:
  result=subprocess.run(['/usr/bin/python3',str(root/name)],stdout=log,stderr=subprocess.STDOUT)
 state['steps'].append({'script':name,'exit':result.returncode,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat()});save()
state['status']='complete' if all(s['exit']==0 for s in state['steps']) else 'script_failure'
state['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
