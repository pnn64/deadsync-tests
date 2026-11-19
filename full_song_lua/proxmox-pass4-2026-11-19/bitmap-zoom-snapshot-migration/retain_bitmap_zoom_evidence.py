"""Retain a reviewed source-derived snapshot correction and its original failures."""
import hashlib
import json
from pathlib import Path
import subprocess

WORK = Path(__file__).resolve().parent
REPO = Path('C:/GitHub/deadsync-fixtures-lua-fleet-20261119')
ROOT = REPO / 'full_song_lua/proxmox-pass4-2026-11-19'
OUT = ROOT / 'bitmap-zoom-snapshot-migration'
PROPOSAL = WORK / 'bitmap-zoom-migration-proposal'
APPLIED = WORK / 'bitmap-zoom-migration-applied/20261119T042604.612602Z'
SNAPSHOT = 'regression-expectations/deadsync-song-lua/a9485a8eaeb14743.snap'
BASE = '866499adb18bf20ad7f102ac401b3df61858fc9f'
def sha(data): return hashlib.sha256(data).hexdigest()
def encoded(value): return (json.dumps(value, indent=2) + '\n').encode()
def git(*args): return subprocess.check_output(['git', '-C', str(REPO), *args]).decode().strip()
def stable(path, data):
    assert len(data) < 50_000_000
    if path.exists(): assert path.read_bytes() == data, path
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

assert git('rev-parse', 'HEAD') == BASE
assert git('status', '--porcelain') == 'M ' + SNAPSHOT
assert sha((REPO / SNAPSHOT).read_bytes()) == 'ae9de3ca4b6a094b506ae6d36577303a056568e8a50dc790810aa87fa307949f'
proposal_bytes = (PROPOSAL / 'proposal.json').read_bytes()
assert sha(proposal_bytes) == 'dc0ea95c04de8822c2f2f876f423eb6e896e3ef829ebdb912b9f2cdea39437de'
proposal = json.loads(proposal_bytes)
receipt_bytes = (APPLIED / 'receipt.json').read_bytes()
assert sha(receipt_bytes) == '0abb80b93ba99aec00241dfa9e271d5f92a06c996039b5515b6e0721f229ecb2'
receipt = json.loads(receipt_bytes)
assert receipt['state'] == 'applied-awaiting-validation' and receipt['exact_three_field_changes']
assert receipt['expected_fixture_head'] == BASE and not receipt['tests_executed']
assert receipt['applied_sha256'] == proposal['proposed']['sha256']
for record in [proposal['original'], proposal['proposed'], *proposal['source_authorities'], *proposal['failing_logs']]:
    data = Path(record['path']).read_bytes()
    assert len(data) == record['bytes'] and sha(data) == record['sha256']
sources = [(path, 'proposal/' + path.relative_to(PROPOSAL).as_posix())
           for path in sorted(PROPOSAL.rglob('*')) if path.is_file()]
sources += [(APPLIED / 'receipt.json', 'application-receipt.json'),
            (WORK / 'apply_bitmap_zoom_migration.py', 'apply_bitmap_zoom_migration.py'),
            (Path(__file__), 'retain_bitmap_zoom_evidence.py')]
files = {OUT / relative: path.read_bytes() for path, relative in sources}
assert len(files) == len(sources)
files[OUT / 'scope.json'] = encoded({
    'schema_version': 1,
    'fixture_base': BASE,
    'snapshot': SNAPSHOT,
    'before_sha256': proposal['original']['sha256'],
    'after_sha256': proposal['proposed']['sha256'],
    'allowed_change': 'Only Overlay(0).state.zoom on three existing rows is neutralized to1.0; native axis scales and all other bytes remain unchanged.',
    'authority': 'The unchanged render-boundary normalization already exists in fleet base2da5562 and was introduced by ancestor a5b4c374ba326708e38e7d9e9cfb6c374cf33a0d.',
    'expected_values_source': 'Reviewed source implementation, independently of runtime test output.',
    'validation_at_publication': 'Applied exact reviewed bytes; unchanged full bitmap_text gate will run against this published snapshot.',
    'native_parity_claim': False,
})
index_path = ROOT / 'evidence-files.json'
old_index = index_path.read_bytes()
index = {row['path']: row for row in json.loads(old_index)}
assert len(index) == len(json.loads(old_index))
for path, data in files.items():
    relative = path.relative_to(REPO).as_posix()
    assert relative not in index
    index[relative] = {'path': relative, 'bytes': len(data), 'sha256': sha(data)}
for path, data in files.items(): stable(path, data)
new_index = encoded(list(index.values()))
if b'\r\n' in old_index: new_index = new_index.replace(b'\n', b'\r\n')
index_path.write_bytes(new_index)
print(json.dumps({'retained_files': len(files), 'snapshot_sha256': receipt['applied_sha256'],
                  'application_receipt_sha256': sha(receipt_bytes), 'native_parity_claim': False}))
