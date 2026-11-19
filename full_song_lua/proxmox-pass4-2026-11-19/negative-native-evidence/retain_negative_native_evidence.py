"""Verify the immutable negative bundle; publish only with --publish after gates."""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import zipfile

WORK = Path(__file__).resolve().parent
SOURCE = WORK / 'negative-evidence-20261119T040831.615986Z'
REPOSITORY = Path('C:/GitHub/deadsync-fixtures-lua-fleet-20261119')
ROOT = REPOSITORY / 'full_song_lua/proxmox-pass4-2026-11-19'
OUT = ROOT / 'negative-native-evidence'
BASE = '0a49b80d8dd1cbc59d86ac764e739537fcc1a79b'

def sha(data): return hashlib.sha256(data).hexdigest()
def encoded(value): return (json.dumps(value, indent=2) + '\n').encode()
def git(*args): return subprocess.check_output(['git', '-C', str(REPOSITORY), *args]).decode().strip()
def stable(path, data):
    assert len(data) < 50_000_000, path
    if path.exists():
        assert path.read_bytes() == data, ('retained bytes differ', path)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

parser = argparse.ArgumentParser()
parser.add_argument('--publish', action='store_true')
args = parser.parse_args()
manifest_bytes = (SOURCE / 'manifest.json').read_bytes()
assert sha(manifest_bytes) == '4fc7cb5431e383607372117c091eed3012814e79861ec8ba1e40c864494ce36d'
manifest = json.loads(manifest_bytes)
bundle = (SOURCE / 'negative-evidence.zip').read_bytes()
assert sha(bundle) == manifest['archive']['sha256'] == 'ac119aabde1690ae88035995f5459e4c0c5d17123e74238312d228810a43c6c4'
assert len(bundle) == manifest['archive']['bytes'] == 13_588_166
members = {row['path']: row for row in manifest['files']}
assert len(members) == len(manifest['files']) == 27
with zipfile.ZipFile(io.BytesIO(bundle)) as archive:
    names = archive.namelist()
    assert len(names) == len(set(names)) and set(names) == set(members)
    for name, expected in members.items():
        path = PurePosixPath(name)
        assert not path.is_absolute() and '..' not in path.parts
        data = archive.read(name)
        assert len(data) == expected['bytes'] and sha(data) == expected['sha256'], name
    verification_bytes = archive.read('verification.json')
    assert json.loads(verification_bytes) == manifest['verification']
verification = manifest['verification']
assert all(row['original_status'] == 'capture_error' for row in verification['e2_original_statuses'])
assert len(verification['e2']) == 2
assert all(row['all_members_hashed'] and row['raw_trace_retained_inside_original_archive'] for row in verification['e2'])
assert verification['sequential_dreambox']['attempts'] == 16
assert verification['sequential_dreambox']['original_status'] == 'native_lua_or_setup_error'
assert verification['candidate_a']['passing_nonzero_gates'] == 13
assert verification['candidate_a']['failing_gates'] == ['test-14']
assert not verification['candidate_a']['passed']
assert not verification['candidate_a']['published_build_passed']

scope = {
    'schema_version': 1,
    'negative_archive_sha256': sha(bundle),
    'external_manifest_sha256': sha(manifest_bytes),
    'native_revision': '663525dcb86eb570d0ef6a2e209678436660ae26',
    'baseline_harness_revision': '9eb6619c0eaf9c3aceabf7348efbb06a7fd37273',
    'e2': 'Both original rejected captures are retained. Authored outCirc evaluation after beat127.5 produces NaN transforms; numeric local vertices with non-finite clip vertices fail the unchanged drawable validator.',
    'sequential_dreambox': 'All16 native Lua failures preserve the original FastEnd.lua early return followed by a local declaration. Authored charts were not edited.',
    'candidate_a': 'The original candidate failed its14th gate after13 nonzero passing gates; its runner was not promoted. Complete original evidence is retained inside the bundle.',
    'native_inputs_modified': False,
    'validation_tolerances_changed': False,
    'negative_classifications_changed': False,
    'fleet_completion_claimed': False,
    'whole_song_parity_proven': False,
}
summary = {'verified_members': len(members), 'archive_sha256': sha(bundle), 'manifest_sha256': sha(manifest_bytes), 'published': False}
if args.publish:
    assert git('rev-parse', 'HEAD') == BASE
    assert not git('status', '--porcelain'), 'fixture worktree must be clean'
    files = {
        OUT / 'negative-evidence.zip': bundle,
        OUT / 'manifest.json': manifest_bytes,
        OUT / 'verification.json': verification_bytes,
        OUT / 'scope.json': encoded(scope),
        OUT / 'retain_negative_native_evidence.py': Path(__file__).read_bytes(),
    }
    index_path = ROOT / 'evidence-files.json'
    old_index = index_path.read_bytes()
    index = {row['path']: row for row in json.loads(old_index)}
    assert len(index) == len(json.loads(old_index))
    for path, data in files.items():
        relative = path.relative_to(REPOSITORY).as_posix()
        assert relative not in index
        index[relative] = {'path': relative, 'bytes': len(data), 'sha256': sha(data)}
    for path, data in files.items(): stable(path, data)
    new_index = encoded(list(index.values()))
    if b'\r\n' in old_index:
        new_index = new_index.replace(b'\n', b'\r\n')
    index_path.write_bytes(new_index)
    summary.update(published=True, retained_files=len(files), fixture_base=BASE)
print(json.dumps(summary, sort_keys=True))
