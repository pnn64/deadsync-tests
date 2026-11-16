"""Guest: native-only validation of source-owned engine/theme candidates."""
import hashlib,json,pathlib,shutil,subprocess,sys
ROOT=pathlib.Path('/opt/song-lua-audit');OUT=ROOT/'pass3-native-routine-controls'
assert not OUT.exists();OUT.mkdir()
proof=json.loads((ROOT/'pass3-native-routine-build/build-proof.json').read_text())
native=ROOT/'routine-native';harness=ROOT/'bin/itgmania-harness-pass3-routine'
theme_proof=json.loads((ROOT/'theme-pump-couple.json').read_text());theme=ROOT/'routine-theme'
def command(args):return subprocess.check_output(list(map(str,args)),text=True).strip()
def sha(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(native/'ITGmania-harness-trace')==proof['native_binary_sha256']
assert sha(harness)==proof['harness_binary_sha256']
assert sha(ROOT/'theme-pump-couple.bundle')==theme_proof['bundle_sha256']
old_theme=ROOT/'harness/vendor/simply-love'
command(['git','-C',old_theme,'fetch','--no-recurse-submodules',ROOT/'theme-pump-couple.bundle','HEAD'])
command(['git','-C',old_theme,'worktree','add','--detach',theme,theme_proof['candidate_commit']])
assert not command(['git','-C',theme,'status','--porcelain'])
link=native/'Themes/Harness Simply Love';assert not link.exists();link.symlink_to(theme,target_is_directory=True)
sys.path.insert(0,str(ROOT));import worker_pass2 as w
w.RESULTS=OUT
proof['theme']=theme_proof
w.write(OUT/'source-proof.json',proof)
jobs=[]
for source,relative in [('routine-style-inputs','styles'),('routine-stats-inputs','routine-stats')]:
 inputs=ROOT/source;dest=ROOT/'Songs/__pass3_controls'/relative
 if dest.exists():
  for path in inputs.rglob('*'):
   if path.is_file():assert sha(path)==sha(dest/path.relative_to(inputs))
 else:shutil.copytree(inputs,dest)
 jobs.extend(json.loads((inputs/'jobs.json').read_text()))
for job in jobs:
 case=OUT/job['id'];case.mkdir()
 simfile=ROOT/'Songs'/job['source_simfile'];assert sha(simfile)==job['simfile_sha256']
 result={'id':job['id'],'profile':job,'source_simfile':job['source_simfile'],'source_snapshot':proof,
  'status':'running','started_at':w.now(),'stages':{}}
 w.write(case/'result.json',result)
 argv=[harness,'song-lua-trace',simfile,'--itgmania-bin',native/'ITGmania-harness-trace',
  '--fallback-theme','Harness Simply Love','--headless','--game',job['game'],'--style',job['style'],
  '--difficulty',job['difficulty'],'--chart-index',str(job['chart_index']),'--until-gameplay-end',
  '--capture-fps','60','--max-events','250000','--timeout','180','--out',case/'native.json']
 if job.get('player_options'):argv+=['--player-options',job['player_options']]
 stage=w.execute(case,'capture',argv,270,memory='6G');result['stages']['capture']=stage
 if stage['exit']==0:
  summary=w.document_summary(case/'native.json');source=summary['input']['native_source']
  assert source['revision']==proof['source']['candidate_commit'] and source['modified_src'] is False
  assert summary['completion']['reason']=='gameplay-exit'
  result['native']=summary;result['status']='native_capture_pass'
  result['trace_sha256']=sha(case/'native.json')
 else:
  log=(case/'capture.log').read_text(errors='replace');result['status']=w.failure_category('capture',stage,log);result['reason']=log[-8000:]
  artifact,facts=w.preserve_diagnostics(case);result['native_failure']=facts
  if artifact:result['artifacts']=[artifact]
 result['finished_at']=w.now();w.write(case/'result.json',result)
 print(json.dumps({'id':result['id'],'status':result['status']}),flush=True)
