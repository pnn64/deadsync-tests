import concurrent.futures,hashlib,json,os,pathlib,shutil,signal,subprocess,time
root=pathlib.Path('/opt/song-lua-audit');out=root/'pass2-video-controls';out.mkdir(exist_ok=True)
source=next((root/'pass2-controls-v2/observer/tmp/itgmania-harness-rs').glob('song-lua-*'))
movies=['Metronogik/bn-4x.mp4','Happy Now/Darkness1.mp4','Young Dumb And Broke/lua/VHS.mp4','My Penny/bn.avi','INAZUMA (Gio)/lua/thunder.mp4']
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(item):
 index,movie=item;case=out/f'movie-{index}';case.mkdir(exist_ok=True);stage=case/'stage'
 assert not stage.exists();shutil.copytree(source,stage,symlinks=True)
 origin=root/'Songs'/movie
 if not origin.exists():
  matches=list((root/'Songs').rglob(pathlib.Path(movie).name));assert len(matches)==1,matches;origin=matches[0]
 dest=stage/'Songs/Harness/Probe'/('movie'+origin.suffix);shutil.copyfile(origin,dest)
 (dest.parent/'default.lua').write_text('return Def.Actor {}\n')
 sim=dest.parent/'control.sm';sim.write_text(sim.read_text()+'\n#BANNER:'+dest.name+';\n')
 trace=stage/'Save/itgmania-harness/song-lua-trace.json';trace.unlink()
 command=['valgrind','--tool=memcheck','--num-callers=24','--leak-check=no','--undef-value-errors=no','--error-exitcode=77','--exit-on-first-error=yes','--log-file='+str(case/'valgrind.log'),str(stage/'ITGmania-harness-trace'),'--game=dance','--theme=itgmania-harness']
 start=time.monotonic();completed=False;timed_out=False
 with (case/'output.log').open('w') as log:
  p=subprocess.Popen(command,cwd=stage,env=dict(os.environ,HOME=str(stage),ITGMANIA_HARNESS_HEADLESS='1'),stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  while p.poll() is None:
   if trace.exists():completed=True;break
   if time.monotonic()-start>360:timed_out=True;break
   time.sleep(.5)
  if p.poll() is None:os.killpg(p.pid,signal.SIGTERM)
  try:p.wait(timeout=10)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
 log=(case/'valgrind.log').read_text(errors='replace')
 result={'movie':str(origin.relative_to(root/'Songs')),'movie_sha256':sha(origin),'binary_sha256':sha(stage/'ITGmania-harness-trace'),'command':command,'exit':p.returncode,'completed':completed,'timed_out':timed_out,'seconds':time.monotonic()-start,'zero_memcheck_errors':'ERROR SUMMARY: 0 errors' in log,'invalid_write':'Invalid write' in log}
 (case/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True);return result
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(run,enumerate(movies)))
(out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
assert all(r['completed'] and r['zero_memcheck_errors'] for r in results)
