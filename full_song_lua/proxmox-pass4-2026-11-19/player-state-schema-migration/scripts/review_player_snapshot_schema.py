#!/usr/bin/env python3
import hashlib
import json
import subprocess
import migrate_player_state_snapshot as migration

expected = migration.rows((migration.EVIDENCE / 'snapshot.before').read_text(encoding='utf-8'))
assert all('life_record_source:' not in value for value in expected.values())
migration.ADDED.add('life_record_source')
review = []
for line in (migration.EVIDENCE / 'captured.tsv').read_text(encoding='utf-8').splitlines():
    test, index, actual = line.split('\t', 2); key = (test, int(index))
    stripped, added = migration.strip_fields(actual)
    assert added['life_record_source'] == 'Meter'
    assert stripped == expected[key], 'unrelated existing scalar changed'
    review.append({'test': test, 'case': int(index), 'all_remaining_bytes_equal': True, 'additional_metadata': {'life_record_source': added['life_record_source']}, 'old_and_stripped_sha256': hashlib.sha256(stripped.encode()).hexdigest()})
source_commit = subprocess.check_output(['git', 'log', '-1', '--format=%H %s', '-S', 'pub life_record_source:', '--', 'crates/deadsync-gameplay/src/player.rs'], cwd=migration.ROOT, text=True).strip()
for name in ['migrate_player_state_snapshot.py', 'player_snapshot_collector.rs', 'run_player_snapshot_gate.py']:
    source = migration.HERE / name; target = migration.EVIDENCE / (name + '.first-attempt')
    assert not target.exists(); target.write_bytes(source.read_bytes())
receipt = {'extra_schema_field': 'life_record_source', 'old_rows_without_field': len(expected), 'captured_rows_verified': len(review), 'source_introducing_commit': source_commit, 'rows': review, 'fixture_mutated': False, 'first_attempt_retained': True}
migration.write_json(migration.EVIDENCE / 'additional-metadata-review.json', receipt)
print(json.dumps(receipt))
