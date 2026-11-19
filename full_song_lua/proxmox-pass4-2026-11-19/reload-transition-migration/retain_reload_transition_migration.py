"""Verify and retain the single native-backed reload snapshot migration."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

WORK = Path(__file__).resolve().parent
REPO = Path('C:/GitHub/deadsync-fixtures-lua-fleet-20261119')
ROOT = REPO / 'full_song_lua/proxmox-pass4-2026-11-19'
OUT = ROOT / 'reload-transition-migration'
SOURCE = WORK / 'modulo-transition-evidence/reload-snapshot-migration'
NAME = 'regression-expectations/deadsync-song-lua/c9dc1ea2bbc62e20.snap'
BASE = '137a6ff3c5d70a9a98221c6d59a3639db3766f86'

def sha(data): return hashlib.sha256(data).hexdigest()
def git(*args): return subprocess.check_output(['git', *args], cwd=REPO)
def encoded(value): return (json.dumps(value, indent=2) + '\n').encode()
def stable(path, data):
    assert len(data) < 50_000_000
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists(): assert path.read_bytes() == data, path
    else: path.write_bytes(data)

assert git('rev-parse', 'HEAD').decode().strip() == BASE
before = git('show', BASE + ':' + NAME)
after = (REPO / NAME).read_bytes()
receipt = json.loads((SOURCE / 'receipt.json').read_bytes())
assert sha(before) == receipt['before_sha256'] == '75e9ed26f40047728cc510fff626b8825976bf4aa9311470ac8111c0b92acd7e'
assert sha(after) == receipt['after_sha256'] == 'ad252682d9d03ff0f219f124fffa4dc4dd4f2f41d444404611998ce75bfcc357'
assert before == (SOURCE / 'before.snap').read_bytes()
assert after == (SOURCE / 'after.snap').read_bytes()
old_lines, new_lines = before.splitlines(keepends=True), after.splitlines(keepends=True)
assert len(old_lines) == len(new_lines)
assert [i + 1 for i, pair in enumerate(zip(old_lines, new_lines)) if pair[0] != pair[1]] == [97]
name = b'test: incoming_style_spooky_reload_and_stage_variants_match'
start = next(i for i, row in enumerate(old_lines) if row.rstrip(b'\r\n') == name) + 1
assert start + 5 == 96
decode = lambda row: bytes(ast.literal_eval(row.decode()))
assert decode(old_lines[96]) == b'1,0,false,true'
assert decode(new_lines[96]) == decode(old_lines[start + 7]).replace(b'2,4,true,false|', b'2,4,false,true|', 1)
assert sha((SOURCE / 'failed-gate.log').read_bytes()) == receipt['failure_log_sha256']
authority_bytes = (WORK / 'modulo-transition-evidence/authority.json').read_bytes()
authority = json.loads(authority_bytes)
assert sha(authority_bytes) == 'e84add9292b24e3f071de2244adf4d32ef916b6978f061acd4f3d2e523529212'
files = {OUT / name: (SOURCE / name).read_bytes() for name in ['before.snap', 'after.snap', 'failed-gate.log', 'receipt.json']}
files[OUT / 'native-authority.json'] = authority_bytes
for item in authority['sources']:
    path = Path(item['path'])
    data = path.read_bytes()
    assert len(data) == item['bytes'] and sha(data) == item['sha256'], path
    leaf = 'ScreenGameplay-in-default.lua' if path.name == 'default.lua' else path.name
    files[OUT / 'native-source' / leaf] = data
files[OUT / 'independent-verification.json'] = encoded({
    'fixture_base': BASE, 'snapshot': NAME, 'before_sha256': sha(before),
    'after_sha256': sha(after), 'changed_lines_one_based': [97],
    'all_other_lines_byte_equal': True, 'source_hashes_verified': True,
    'expected_child_resources_copied_from_existing_default_arrows_case': True,
    'old_decoded': decode(old_lines[96]).decode(), 'new_decoded': decode(new_lines[96]).decode(),
    'final_transition_gate_pending': True,
    'scope': 'Only the retained child tree of the hidden reload intro changes; no native trace or statistics expectation is modified.'})
files[OUT / 'retain_reload_transition_migration.py'] = Path(__file__).read_bytes()
for path, data in files.items(): stable(path, data)
index_path = ROOT / 'evidence-files.json'
index_bytes = index_path.read_bytes()
assert b'\r\n' in index_bytes
records = json.loads(index_bytes)
index = {item['path']: item for item in records}
assert len(index) == len(records)
for path, data in files.items():
    relative = path.relative_to(REPO).as_posix()
    assert relative not in index, relative
    index[relative] = {'path': relative, 'bytes': len(data), 'sha256': sha(data)}
index_path.write_bytes(encoded(list(index.values())).replace(b'\n', b'\r\n'))
print(json.dumps({'retained_files': len(files), 'changed_snapshot_lines': [97], 'all_other_lines_byte_equal': True, 'after_sha256': sha(after)}))
