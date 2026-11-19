"""Independently verify and retain the reviewed additive runtime snapshot migration."""
import hashlib
import json
from pathlib import Path
import subprocess
import migrate_player_state_snapshot as migration

WORK = Path(__file__).resolve().parent
PRODUCT = WORK.parents[1]
REPOSITORY = Path('C:/GitHub/deadsync-fixtures-lua-fleet-20261119')
ROOT = REPOSITORY / 'full_song_lua/proxmox-pass4-2026-11-19'
OUT = ROOT / 'player-state-schema-migration'
RELATIVE = 'regression-expectations/deadsync-song-lua/72c431600eddf935.snap'

def sha(data): return hashlib.sha256(data).hexdigest()
def git(*args): return subprocess.check_output(['git', '-C', str(REPOSITORY), *args])

before = (migration.EVIDENCE / 'snapshot.before').read_bytes()
after = migration.SNAPSHOT.read_bytes()
assert sha(before) == '049b758d3c6e6c8f2b0e4a99027f036377b6336a591d6a7b1a9dff2593411caa'
assert sha(after) == '839a8061762cfe6796af0ac5da077ad27a42354ef9b7ff763fc9fb54a628315b'
old_rows = migration.rows(before.decode())
new_rows = migration.rows(after.decode())
assert len(old_rows) == len(new_rows) == 130 and old_rows.keys() == new_rows.keys()
for key, value in new_rows.items():
    stripped, additions = migration.strip_fields(value)
    assert stripped == old_rows[key], key
    assert set(additions) == migration.ADDED
captured = {}
for line in (migration.EVIDENCE / 'captured.tsv').read_text(encoding='utf-8').splitlines():
    test, index, actual = line.split('\t', 2)
    key = (test, int(index))
    assert key not in captured
    captured[key] = actual
assert captured == new_rows
support_before = (migration.EVIDENCE / 'reference_test.rs.before').read_bytes()
assert migration.SUPPORT.read_bytes() == support_before
assert sha(support_before) == '64002ab8a09416d74d13a2c19679f6efb9acf452edc10ef90cfab8e7af1e41e9'
final = json.loads((migration.EVIDENCE / 'final-unmodified.json').read_text())
assert final['exit_code'] == 0 and final['passed'] and not final['temporary_collector']
assert sha((migration.EVIDENCE / 'final-unmodified.log').read_bytes()) == final['log_sha256']
committed = git('show', 'HEAD:' + RELATIVE)
assert committed.replace(b'\r\n', b'\n') == before.replace(b'\r\n', b'\n')

sources = []
for source_name, destination_name in [('player-state-schema-migration', 'rejected-first-attempt'), ('player-state-schema-migration-v2', 'validated-migration')]:
    for source in sorted((WORK / source_name).rglob('*')):
        if source.is_file(): sources.append((source, Path(destination_name) / source.relative_to(WORK / source_name)))
for name in ['migrate_player_state_snapshot.py', 'player_snapshot_collector.rs', 'run_player_snapshot_gate.py', 'review_player_snapshot_schema.py', 'retain_player_state_migration.py']:
    sources.append((WORK / name, Path('scripts') / name))
for source, relative in sources:
    data = source.read_bytes()
    assert len(data) < 50_000_000
    target = OUT / relative
    if target.exists(): assert target.read_bytes() == data, target
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
destination = REPOSITORY / RELATIVE
if destination.exists():
    assert destination.read_bytes().replace(b'\r\n', b'\n') in (before.replace(b'\r\n', b'\n'), after)
destination.parent.mkdir(parents=True, exist_ok=True)
git('update-index', '--no-skip-worktree', '--', RELATIVE)
destination.write_bytes(after)
summary = {'snapshot_path': RELATIVE, 'before_sha256': sha(before), 'after_sha256': sha(after),
    'old_rows_verified': 130, 'existing_value_changes': 0, 'new_fields_only': sorted(migration.ADDED),
    'temporary_collector_restored_byte_for_byte': True, 'unmodified_live_gameplay_tests': 16,
    'native_observations_replaced': False, 'retained_files': len(sources)}
(OUT / 'independent-verification.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
index_path = ROOT / 'evidence-files.json'
index = {item['path']: item for item in json.loads(index_path.read_text())}
for path in sorted(OUT.rglob('*')):
    if not path.is_file(): continue
    data = path.read_bytes()
    relative = path.relative_to(REPOSITORY).as_posix()
    index[relative] = {'path': relative, 'bytes': len(data), 'sha256': sha(data)}
index_path.write_text(json.dumps(list(index.values()), indent=2) + '\n', encoding='utf-8')
print(json.dumps(summary, sort_keys=True))
