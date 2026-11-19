"""Independently verify restricted statistics rows and retain their source basis."""
import ast
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess

WORK = Path(__file__).resolve().parent
PRODUCT = WORK.parents[1]
REPO = PRODUCT.parent / 'deadsync-fixtures-lua-fleet-20261119'
NATIVE = PRODUCT.parent / 'itgmania-harness/vendor/itgmania'
ROOT = REPO / 'full_song_lua/proxmox-pass4-2026-11-19'
OUT = ROOT / 'played-stage-snapshot-migration'
PROPOSAL = WORK / 'played-stage-history-evidence/statistics-snapshot-proposal'
BASE = '234352ae735a4ec78230f2139e56fa3be734bedc'
NAME = 'regression-expectations/deadsync-song-lua/a74e87153021edf1.snap'
def sha(data): return hashlib.sha256(data).hexdigest()
def git(repo, *args): return subprocess.check_output(['git', *args], cwd=repo)
def encoded(value): return (json.dumps(value, indent=2) + '\n').encode()
def stable(path, data):
    assert len(data) < 50_000_000
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists(): assert path.read_bytes() == data, path
    else: path.write_bytes(data)
def row_values(line):
    match = re.fullmatch(r'\((\d+), (\d+), \[(.*)\]\)', line.decode().strip())
    assert match
    tokens = re.findall(r'String\(\[[^]]*\]\)|Number\(\d+\)|Boolean\((?:true|false)\)|Nil', match[3])
    assert ', '.join(tokens) == match[3]
    def decode(token):
        if token.startswith('String('): return bytes(ast.literal_eval(token[7:-1])).decode()
        if token.startswith('Number('): return struct.unpack('<d', struct.pack('<Q', int(token[7:-1])))[0]
        if token.startswith('Boolean('): return token == 'Boolean(true)'
        return None
    return [decode(token) for token in tokens]

assert git(REPO, 'rev-parse', 'HEAD').decode().strip() == BASE
before = git(REPO, 'show', BASE + ':' + NAME)
after = (REPO / NAME).read_bytes()
assert sha(before) == 'a52e4d833073a6896a57ad341bc6c9e64e2821a25675d53605657ca8ddf8224f'
assert sha(after) == 'c7565d21639378ae8df497127efe4e1a0a5293f4190d58a679fd6acd9222650b'
assert before == (PROPOSAL / 'before.snap').read_bytes() and after == (PROPOSAL / 'after.snap').read_bytes()
receipt_bytes = (PROPOSAL / 'receipt.json').read_bytes()
assert sha(receipt_bytes) == '408aa2e09d4ca560e0b649fe3e7934b1af57b0f3d5e362a967786a565437590f'
receipt = json.loads(receipt_bytes)
assert receipt['actual_output_used_as_expectation'] is False
old_lines, new_lines = before.splitlines(keepends=True), after.splitlines(keepends=True)
changed = [i + 1 for i, pair in enumerate(zip(old_lines, new_lines)) if pair[0] != pair[1]]
assert len(old_lines) == len(new_lines) and changed == list(range(4, 32))
assert [item['case'] for item in receipt['changed_rows']] == list(range(1, 29))
for item in receipt['changed_rows']:
    old, new = row_values(old_lines[item['line'] - 1]), row_values(new_lines[item['line'] - 1])
    assert old == item['before_values'] and new == item['after_values']
    if item['case'] == 1:
        assert len(old) == len(new) == 26
        assert all(old[i] == new[i] for i in range(26) if i not in {1, 2, 3, 4, 5, 18})
        assert old[5] == 1 and new[5] == 0 and old[18] == 125.25 and new[18] == 0
        for index, key in [(1, '__songlua_steps_seconds'), (2, '__songlua_alive_seconds'), (3, '__songlua_alive_seconds'), (4, '__songlua_alive_seconds')]:
            assert key not in old[index].split(',') and new[index] == ','.join(sorted(old[index].split(',') + [key]))
    elif item['case'] == 28:
        assert len(old) == len(new) == 9
        assert all(old[i] == new[i] for i in range(9) if i not in {5, 6})
        assert old[5:7] == [1, 1] and new[5:7] == [100, 100]
    else:
        assert len(old) == 3 and len(new) == 4 and old[:2] == new[:2]
        accepted = item['case'] not in {2, 3, 4, 20, 21, 22, 25, 26, 27}
        assert new[2:] == [accepted, accepted]
assert sha((PROPOSAL / 'before-source.rs').read_bytes()) == receipt['old_source_sha256']
assert sha((PROPOSAL / 'after-source.rs').read_bytes()) == receipt['new_source_sha256']
assert (PRODUCT / 'crates/deadsync-song-lua/tests/statistics.rs').read_bytes() == (PROPOSAL / 'after-source.rs').read_bytes()
assert git(NATIVE, 'rev-parse', 'HEAD').decode().strip() == receipt['native_commit'] == '663525dcb86eb570d0ef6a2e209678436660ae26'
files = {OUT / name: (PROPOSAL / name).read_bytes() for name in ['before.snap', 'after.snap', 'before-source.rs', 'after-source.rs', 'receipt.json']}
native_verification = []
for item in receipt['authority']:
    data = (NATIVE / item['path']).read_bytes()
    pinned = git(NATIVE, 'show', receipt['native_commit'] + ':' + item['path'])
    normalized = data.replace(b'\r\n', b'\n')
    pinned_normalized = pinned.replace(b'\r\n', b'\n')
    assert sha(data) == item['sha256'] and normalized == pinned_normalized, item['path']
    native_verification.append({'path': item['path'], 'retained_bytes': len(data),
        'retained_sha256': sha(data), 'pinned_blob_bytes': len(pinned), 'pinned_blob_sha256': sha(pinned),
        'raw_bytes_equal': data == pinned, 'equal_after_crlf_normalization': True,
        'normalized_sha256': sha(normalized)})
    for region in item['regions']:
        assert '\n'.join(data.decode().splitlines()[region['first_line'] - 1:region['last_line']]) == region['text']
    files[OUT / 'native-source' / item['path']] = data
files[OUT / 'prepare_statistics_snapshot_proposal.py'] = (WORK / 'prepare_statistics_snapshot_proposal.py').read_bytes()
failed = WORK / 'corpus-audit-history-controls-20261119T033312Z/statistics.log'
assert sha(failed.read_bytes()) == '017effcb8bbbdcc0cfacc324b9402957d7b6cc687c6a41f702b221c6b95d0c81'
files[OUT / 'failed-gate.log'] = failed.read_bytes()
files[OUT / 'independent-verification.json'] = encoded({'before_sha256': sha(before), 'after_sha256': sha(after),
    'changed_lines': changed, 'all_unrelated_rows_byte_equal': True, 'changed_field_allowlist_checked': True,
    'native_sources': native_verification, 'native_files_equal_after_crlf_normalization': True,
    'source_input_identity_recipe_reviewed': True,
    'expected_output_harvested_from_run': False, 'final_full_statistics_gate_pending': True})
files[OUT / 'retain_played_stage_snapshot.py'] = Path(__file__).read_bytes()
for path, data in files.items(): stable(path, data)
index_path = ROOT / 'evidence-files.json'
raw = index_path.read_bytes(); assert b'\r\n' in raw
records = json.loads(raw); index = {item['path']: item for item in records}; assert len(index) == len(records)
for path, data in files.items():
    relative = path.relative_to(REPO).as_posix(); assert relative not in index
    index[relative] = {'path': relative, 'bytes': len(data), 'sha256': sha(data)}
index_path.write_bytes(encoded(list(index.values())).replace(b'\n', b'\r\n'))
print(json.dumps({'retained_files': len(files), 'changed_rows': 28, 'all_unrelated_rows_byte_equal': True, 'after_sha256': sha(after)}))
