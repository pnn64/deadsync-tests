import collections,datetime,hashlib,json,pathlib,shutil,subprocess
from remote import WORK
store=pathlib.Path('C:/GitHub/deadsync/tests/fixtures/full_song_lua')
old=store/'proxmox-audit-2026-11-15';out=store/'proxmox-pass2-2026-11-15';out.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(name,value):(out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def cell(value):return str(value).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('|','\\|').replace('\n',' ')
baseline=read(old/'case-ledger.json');primary=read(WORK/'all-results.json');extra=read(WORK/'extra-results.json');final=read(WORK/'final-results.json')
baseline_ids={r['id'] for r in baseline};jobs=read(WORK/'jobs.json');latest={}
for r in primary+extra:
 key=r['id'].removesuffix('-memory26')
 if key in baseline_ids:latest[key]=r
for r in final:
 key=r['id'].removesuffix('-memory26')
 if key in latest and latest[key]['id']==r['id']:latest[key]=r

def classified_status(r):
 status=r['status']
 if status=='native_capture_error':
  summaries=[n.get('summary',{}) for n in r.get('native_failure',[])]
  if any(n.get('script_errors') for n in summaries):return 'native_lua_error'
  if any(any(k.startswith('dropped_') and isinstance(v,(int,float)) and v>0 for k,v in n.items()) for n in summaries):return 'capture_observation_limit'
 return status

def missing(r):
 name=r['source_simfile'];status=classified_status(r);comparison=r.get('comparison',{})
 if status=='pass':return ''
 if 'KENPO' in name:return 'Seven same-frame node-order differences remain. Preserve native traversal/table allocation order; see the first-audit permutation proof. No comparator sorting was added.'
 if 'Velvet' in name:return 'Automatic Lua GC changes allocation/table iteration order. The separately captured stopped-GC profile passes; it does not establish parity for automatic GC.'
 if 'Megalovania' in name:return 'ScreenGameplay:PauseGame currently records a Lua flag but does not pause the gameplay/audio runtime. Native Player::Update advances actor children and then skips judgments while paused; descendant Judgment timing diverges around the authored pause.'
 if 'After Dark/' in name:return 'The roll frame-clock fix removes 1,065 of 1,240 differences in the same fresh capture. The remaining 175 are a subset of the original mismatches: hold-feedback timing near beat 479.657, with native HoldJudgment time 0.711258 seconds versus DeadSync 0.8. Hold-tail feedback dispatch/frame ordering still needs alignment.'
 if status=='parity_failure':return 'Remaining mismatch fields: '+', '.join(comparison.get('mismatch_fields',{}))+'. Inspect retained native/deadsync values before changing runtime behavior; full compressed reports remain on the VM.'
 if 'Anxiety/' in name:return 'The P1-to-versus join/reload control now passes, including roster, style, and positions. This authored native run fails in Simply Love TrackFailTime.lua:121 after P2 joins without autoplay/stream metrics. A clean native reference and a complete inactive-player profile are still needed. Unjoin and physical-P2-origin joins are not established.'
 if 'ULTIMATE' in name:return 'Inline-comma parsing is fixed in RSSP, and BackgroundEffect subscriber paths are fixed. Native now reports an overlay.lua tween overflow, including with a fixed 1/60-second update delta; this prevents accepting a complete clean oracle.'
 if 'Sequential Dreambox' in name:return "New native script-error observation exposes FastEnd.lua:47: '<eof>' expected near 'local'. The original zero-Lua-call pass was invalid; the authored script needs correction before parity can be assessed."
 if 'ChikuTaku' in name:return 'Authored native movie setup passes a nil musicrate to Sprite.rate. Supply/resolve the song dependency before accepting a native oracle.'
 if 'Haxo' in name:return 'Authored native effectmagnitude call has too few numeric arguments; the song needs a valid native execution before comparison.'
 if 'Happiness' in name:return 'Native diva.lua:1092 reads an exhausted break-length table after foreground restart. Resolve the authored lifecycle error before accepting a native oracle.'
 if 'Bank Account' in name:return 'The single-player profile accesses an absent PlayerP2. A separate versus capture passes; it does not replace this primary profile.'
 if 'Lesson by DJ' in name:return 'The source SM has no selectable chart (malformed NOTES header). Repair the corpus simfile before a full native run.'
 if '/saved/' in name and 'Cursed' in name:return 'The saved chart is missing its music dependency; the native capture never yields a valid completed reference.'
 errors=[e for item in r.get('native_failure',[]) for e in item.get('summary',{}).get('script_errors',[])]
 if errors:return 'Native reports '+str(errors[0].get('message',errors[0]))[:650]+'. A clean native run is required before accepting a fixture.'
 drops=[d for n in r.get('native_failure',[]) if (d:={k:v for k,v in n.get('summary',{}).items() if k.startswith('dropped_') and isinstance(v,(int,float)) and v>0})]
 if status=='capture_observation_limit' or drops:
  additional=' Capture postprocessing also ended as '+status+' at '+str(r.get('stages',{}).get('capture',{}).get('memory_limit','the recorded limit'))+'.' if 'resource' in status else ''
  return 'Native reaches gameplay exit but the bounded trace loses observations: '+json.dumps(drops)+'. A streaming capture/replay path and a sufficient observation budget are needed; the truncated trace is rejected.'+additional
 if any(x in status for x in ['resource','timeout','observation','archive_error']):
  limits={k:{x:s.get(x) for x in ['memory_limit','timeout_seconds','elapsed_seconds','exit']} for k,s in r.get('stages',{}).items()}
  return 'No complete comparison under the recorded resource/observation limits. Streaming trace parsing/replay or a larger isolated budget is still needed; do not infer a semantic verdict. Limits: '+json.dumps(limits,separators=(',',':'))
 if status=='running':return 'Attempt still running; this report is provisional.'
 return r.get('reason','A complete verified native capture and replay are still needed.')[-900:]

ledger=[]
for b in baseline:
 r=latest.get(b['id']);row={'id':b['id'],'source_simfile':b['source_simfile'],'previous_status':b['status'],'previous_mismatches':b.get('mismatches'),'fresh_capture_this_pass':r is not None,'final_revision_replayed':bool(r and r.get('native_capture_reused'))}
 if r:row.update(status=classified_status(r),raw_attempt_status=r['status'],attempt_id=r['id'],result_directory=r.get('result_directory','pass2-results'),ip=r.get('ip'),mismatches=r.get('comparison',{}).get('mismatch_count'),missing=missing(r))
 else:row.update(status=b['status'],mismatches=b.get('mismatches'),missing='Historical result only; not rerun against this patch set.')
 ledger.append(row)
current_failures=[r for r in ledger if r['status']!='pass']
valid_controls={'feedback-apollo-v2','feedback-megalovania-v2','roll-long-frame','join-reload-v3'}
supplemental={r['id'].removesuffix('-memory26'):r for r in primary+extra+final if r['id'].removesuffix('-memory26') not in baseline_ids and (not r['source_simfile'].startswith('__pass2_controls/') or r['id'] in valid_controls)}
captured={r['id'].removesuffix('-memory26'):r for r in primary+extra if not r['source_simfile'].startswith('__pass2_controls/') or r['id'] in valid_controls}
expected_final={r['id'] for r in captured.values() if r['status'] in ['pass','parity_failure']}
expected_final.update(r['id'] for r in final)
if (WORK/'paint-sm-resource-retry.json').exists():expected_final.add(read(WORK/'paint-sm-resource-retry.json')['id'])
finished_final={r['id'] for r in final if r.get('finished_at') and r['status']!='running'}
pending_final=sorted(expected_final-finished_final)
unfinished=any(r['status']=='running' for r in primary+extra+final) or len(primary)<len(jobs) or pending_final
summary={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'provisional' if unfinished else 'complete',
 'baseline_counts':dict(collections.Counter(r['status'] for r in baseline)),
 'latest_available_counts':dict(collections.Counter(r['status'] for r in ledger)),
 'fresh_primary_cases':len(latest),'historical_primary_cases_not_rerun':len(baseline)-len(latest),
 'previously_nonpassing_now_pass':sum(b['status']!='pass' and b['id'] in latest and classified_status(latest[b['id']])=='pass' for b in baseline),
 'previously_passing_now_nonpass':sum(b['status']=='pass' and b['id'] in latest and classified_status(latest[b['id']])!='pass' for b in baseline),
 'primary_attempts_recorded':len(primary),'planned_primary_and_supplemental_attempts':len(jobs),
 'final_replays_expected':len(expected_final),'final_replays_pending':pending_final,
 'new_passing_archives_published':len(read(WORK/'published-archives.json')),
 'fresh_primary_counts':dict(collections.Counter(r['status'] for r in ledger if r['fresh_capture_this_pass'])),
 'baseline_nonpass_transitions':dict(collections.Counter(b['status']+' -> '+classified_status(latest[b['id']]) for b in baseline if b['status']!='pass' and b['id'] in latest)),
 'coverage':'One selected chart/style per simfile. Implemented diagnostic comparisons only; complete rendering/production parity is not proven.'}
save('summary.json',summary);save('case-ledger.json',ledger);save('current-failures.json',current_failures)
save('primary-attempts.json',primary);save('extra-attempts.json',extra);save('final-replays.json',final);save('supplemental-results.json',list(supplemental.values()))
save('failure-details.json',[r for r in latest.values() if r['status']!='pass'])
for name in ['jobs.json','fleet.json','fleet-started.json','source-snapshot.json','final-validation-source-snapshot.json','final-source-equivalence.json','initial-state.json','published-archives.json','heavy-redistribution.json','resource-retries.json','james-resource-retries.json','host-oom-evidence.json','idle-shutdown.json','helper-preservation.json','worker14-recovery.json','manual-player-refresh-proof.json','feedback-mismatches-full.json','ba1dd6297cd6aae0-feedback-clocks.json','c3e0c410f04c30dd-feedback-clocks.json','fbe89f6bae9565a6-feedback-clocks.json','afterdark-final-mismatches.json','final-light-completion.json','worker1305-preservation.json']:
 if (WORK/name).exists():shutil.copyfile(WORK/name,out/name)
for name in ['subscriber-fix-source-snapshot.json','join-observer-source-snapshot.json','join-layout-source-snapshot.json','roll-clock-source-snapshot.json']:
 if (WORK/name).exists():shutil.copyfile(WORK/name,out/name)
for name in ['worker1302-preservation.json','worker1303-preservation.json','worker1314-preservation.json','worker1315-preservation.json','local-validation.json','user-edits-preserved.json','fixture-pushes.json','repository-pins.json','fleet-final-shutdown.json','fixture-catalog-validation.json','deadsync-repairs-commit.json','followup-redistribution.json','james-fixed-redistribution.json','report-validation.json','arrowquest-replay-pressure.json']:
 if (WORK/name).exists():shutil.copyfile(WORK/name,out/name)
shutil.copytree(WORK/'native-controls-evidence',out/'native-controls-evidence',dirs_exist_ok=True)
tooling=out/'tooling';tooling.mkdir(exist_ok=True)
for name in ['worker_pass2.py','final-replay-worker.py','run-final-light.py','queue-final-active.py','recover-worker14.py','resume-native14.py','redistribute-heavy.py','redistribute-followup.py','redistribute-james-fixed.py','start-resource-retries.py','collect.py','collect-extra.py','collect-final.py','publish-passing.py','commit-fixture-batches.py','validate-fixture-catalog.py','validate-pass2-report.py','retire-completed.py','build-pass2-report.py','native-controls.py','video-controls.py']:
 if (WORK/name).exists():shutil.copyfile(WORK/name,tooling/name)
shutil.copyfile(WORK/'remote.py',tooling/'remote.py')
if (WORK/'fof-redistribution.json').exists():shutil.copyfile(WORK/'fof-redistribution.json',out/'fof-redistribution.json')
shutil.copyfile(WORK/'redistribute-fof.py',tooling/'redistribute-fof.py')
if (WORK/'paint-sm-resource-retry.json').exists():shutil.copyfile(WORK/'paint-sm-resource-retry.json',out/'paint-sm-resource-retry.json')
shutil.copyfile(WORK/'retry-paint-sm-final.py',tooling/'retry-paint-sm-final.py')
lines=['# Song Lua parity repair pass','',f"Status: **{summary['status']}**. This pass targets the 59 non-passing primary cases from the 503-case audit, two Sharkmode regressions, Sequential Dreambox, and six alternate-profile controls. Additional reduced native controls isolate observer, reload, and feedback behavior.",'',
 f"Fresh primary cases recorded: **{len(latest)}**. Historical primary cases not rerun: **{503-len(latest)}**. The latest-available 503-case ledger is **not** a fresh full-corpus result for this revision.",'',
 '| Latest available primary result | Cases |','| --- | ---: |']
lines += [f'| {k} | {v} |' for k,v in sorted(summary['latest_available_counts'].items())]
lines += ['', f"Previously non-passing primary cases now passing: **{summary['previously_nonpassing_now_pass']} of 59**. Previously passing primary cases now rejected: **{summary['previously_passing_now_nonpass']}**. This includes the newly observed native syntax failure in Sequential Dreambox.", '', '## Fresh primary results', '', '| Fresh result | Cases |', '| --- | ---: |']
lines += [f'| {k} | {v} |' for k,v in sorted(summary['fresh_primary_counts'].items())]
lines += ['', '## Repairs and evidence','',
 '- DeadSync: classify lowercase `getaux` as a query; initialize effect clocks before the first update; preserve logical background entrypoint spelling; carry joined-player roster/style/positions through gameplay reload; observe newly returned style objects; preserve BackgroundEffect wrapper paths for subscribers; drain autoplay rolls using the native frame delta.',
 '- RSSP `5b0284eed201e6511265f9e295e3520e12ac1536` (0.4.291): retain inline measure delimiters when parsing note rows. Ultimate now has the complete chart rather than a one-measure parse.',
 '- Harness: preserve fluent PlayerOptions/SongOptions return identity, record LastSeenVideoDriver, observe native Lua load/runtime/tween failures, isolate post-gameplay transition errors, retain crash diagnostics, and reduce avoidable JSON/file copies. Imported traces with observed script errors are rejected too.',
 '- Native ITGmania `008bfcfef57a107eaafe08b4de7d9d42c6dd1e2f`: pad movie surfaces for SIMD color conversion while retaining logical dimensions. Five movie controls have zero Valgrind errors; fresh full-song cases test the formerly crashing videos.',
 '- New native controls cover initial clocks, fluent options, preferences, malformed source rejection, join/reload, and feedback clocks. The final join control verifies both player positions and style queries. A roll control using a fixed 0.2-second update delta passes; the real-song captures provide the irregular-frame regression evidence.',
 '- The manual-player native golden is refreshed from the native oracle. The harness projection had 171 decimal-only differences, all with identical float32 bits. The full DeadSync fixture already had the same numeric values. Exact geometry comparisons remain enabled.',
 '', '## Reproducibility and limits','',
 'The 15 fresh workers are VMs 1301–1315 with two CPUs each; 1316 is a temporary four-CPU build/control helper. Resource retries raise individual budgets from 6 GiB to 26, 42, or 50 GiB. Complete command lines, event caps, timeouts, native profiles, hashes, and failed attempts are retained in the JSON records. The old fleet and all disks remain available.',
 'Native captures use the new harness/native source snapshot. Later DeadSync fixes replay those exact, hash-verified fresh captures. `final-replays.json` records the final runner SHA and its source snapshot separately from the capture snapshot; earlier results are not relabeled as final. The source diff includes seven pre-existing user edits to actor capture boxing, preserved separately and excluded from the DeadSync repair commit.',
 'One host-wide memory exhaustion killed VM 1314 after the native raw trace was published, during capture postprocessing. Finished workers were shut down; the completed raw trace was hash-verified and checked for clean gameplay exit, zero drops/errors, null renderer, and the expected native revision. Recovery uses the existing song-lua-analyze command with the two provenance assignments normally made by capture_in (source_simfile and command_observer). Archive and replay validation remain enabled; the original raw trace is retained. This is an infrastructure interruption, not a song verdict. An initial final-replay helper used a non-content-addressed filename; those rejected attempts are retained and repeated with the correct archive name.',
 'Pass means all implemented diagnostic comparisons succeeded. Production preparation and complete rendering parity remain unproven. The original audit’s XML/entrypoint/profile guards and zero-actor coverage limits still apply to historical cases. No comparator tolerance, event ordering, corpus Lua source, or authored simfile was changed to obtain a pass.',
 '', '## Current primary failures','', '| Song simfile | Status | Mismatches | Missing behavior or evidence |','| --- | --- | ---: | --- |']
for r in current_failures:
 lines.append('| '+ ' | '.join(cell(x) for x in [r['source_simfile'],r['status'],r['mismatches'] if r['mismatches'] is not None else '-',r['missing']])+' |')
lines += ['', '## Supplemental profiles and controls','', 'Earlier invalid reduced controls and intermediate join-control failures remain in `extra-attempts.json`. The first feedback probes incorrectly used SetUpdateFunction on Def.Actor; the corrected ActorFrame probes are the valid controls below. Alternate profiles do not replace the primary case in the 503-case ledger.', '', '| Case | Source | Latest result | Mismatches | Missing behavior or evidence |', '| --- | --- | --- | ---: | --- |']
for key,r in sorted(supplemental.items()):
 lines.append('| '+ ' | '.join(cell(x) for x in [key,r['source_simfile'],classified_status(r),r.get('comparison',{}).get('mismatch_count','-'),missing(r)])+' |')
lines += ['', 'See [all 503 cases](case-ledger.json), [full failure details](failure-details.json), [final replay results](final-replays.json), and [supplemental profiles](supplemental-results.json). Native candidates and full compressed comparison reports remain on their recorded VMs. Accepted fixtures are listed with verified compressed and decoded hashes in [published-archives.json](published-archives.json).','']
for prefix in ['Native captures use ', 'One host-wide ', 'Pass means ']:
 index=next(i for i,line in enumerate(lines) if line.startswith(prefix));lines.insert(index,'')
index=lines.index('## Current primary failures')
lines[index:index]=['Committed source and dependency revisions are recorded in [repository pins](repository-pins.json). Targeted DeadSync checks, the complete harness test suite, and RSSP tests passed; [local validation](local-validation.json) records their counts and ignored tests. The entire DeadSync application test suite was not rerun.','']
index=lines.index('## Supplemental profiles and controls')+2
lines[index:index]=['The `fixed60` profiles set the native `ConstantUpdateDeltaSeconds` preference to 1/60 second. This fixes the update delta; it does not impose a real-time 60 FPS frame cap. The long-frame roll control similarly uses a 0.2-second update delta.','']
(out/'README.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps(summary,indent=2))
