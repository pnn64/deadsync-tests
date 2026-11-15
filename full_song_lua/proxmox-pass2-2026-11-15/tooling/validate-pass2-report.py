"""Validate complete coverage and exact links between accepted runs and fixtures."""
import collections,datetime,json,pathlib
from remote import WORK
out=pathlib.Path('C:/GitHub/deadsync/tests/fixtures/full_song_lua/proxmox-pass2-2026-11-15')
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
summary=read(out/'summary.json');ledger=read(out/'case-ledger.json');primary=read(out/'primary-attempts.json')
final=read(out/'final-replays.json');jobs=read(WORK/'jobs.json');published=read(WORK/'published-archives.json')
assert summary['status']=='complete' and summary['final_replays_pending']==[]
assert len(ledger)==len({r['id'] for r in ledger})==503
assert len(primary)==len({r['id'] for r in primary})==len(jobs)==68
assert {r['id'] for r in primary}=={r['id'] for r in jobs}
assert all(r['fresh_capture_this_pass'] for r in ledger if r['previous_status']!='pass')
assert sum(r['fresh_capture_this_pass'] for r in ledger)==62
assert all(r['status']!='running' and r.get('finished_at') for r in primary+final+read(out/'extra-attempts.json'))
assert len(final)==len({r['id'] for r in final})
proof=read(WORK/'final-source-equivalence.json')
assert proof['committed_source_matches_final_runner']
for r in final:
 assert r['runner_sha256']==proof['runner_sha256']
 assert r['source_snapshot']==read(WORK/'final-validation-source-snapshot.json')
 assert r['native_capture_reused'] and r.get('finished_at')
 if r['status']=='pass':
  assert r['comparison']['archive_accepted'] and r['comparison']['mismatch_count']==0
  assert r['stages']['replay']['exit']==0
accepted={a['sha256'] for r in final if r['status']=='pass' for a in r['artifacts'] if '/accepted/' in a['file']}
assert accepted=={r['sha256'] for r in published},'published archive missing a passing final revision replay'
assert all(r['decoded_sha256_verified'] for r in published)
freshpass=[r for r in ledger if r['fresh_capture_this_pass'] and r['status']=='pass']
assert all(r['final_revision_replayed'] for r in freshpass)
assert read(out/'current-failures.json')==[r for r in ledger if r['status']!='pass']
assert collections.Counter(r['status'] for r in ledger)==summary['latest_available_counts']
result={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'unique_primary_ledger_cases':503,'fresh_primary_cases':62,'historical_primary_cases':441,'planned_jobs_completed':68,'all_59_previous_nonpassing_cases_attempted':True,'final_replays':len(final),'accepted_archives_matching_final_passes':len(accepted),'all_fresh_passes_replayed_with_final_runner':True,'runner_sha256':proof['runner_sha256']}
(WORK/'report-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
