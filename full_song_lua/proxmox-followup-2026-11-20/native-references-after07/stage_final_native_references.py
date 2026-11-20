"""Verify accepted archives and copy their exact bytes/provenance for fixture staging."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import shutil
import subprocess
import zipfile
import zstandard

ROOT = Path(__file__).resolve().parents[2]
TASK = Path(__file__).resolve().parent
NATIVE = TASK / 'real-song-reference-20261120'
FIXTURE = ROOT / 'tests/fixtures'
STORE = FIXTURE / 'full_song_lua'
OUT = STORE / 'proxmox-followup-2026-11-20/native-references-after07'
SOURCE_COMMIT = 'af6a6c9e045f5dfb13abe38bd4eb58d7326f2e26'

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def git(*args, cwd=FIXTURE):
    return subprocess.check_output(['git', *args], cwd=cwd, text=True).strip()

assert git('branch', '--show-current') == 'main'
assert git('rev-parse', 'HEAD') == 'd2f26868ef5e804b23a5d734f6933c092e677590'
assert not git('status', '--porcelain'), 'preserve pre-existing fixture work'
assert git('rev-parse', 'HEAD', cwd=ROOT) == SOURCE_COMMIT
assert not OUT.exists()
release_path = NATIVE / 'control-packs-after07-release.json'
assert sha(release_path) == 'bd9c261608982fc281a4960b2f9979d1c194dffcb34240050c628d8cf9a18df9'
release = json.loads(release_path.read_bytes())
assert release['guest_ownership_released_to_parent'] and not release['guest_release_check']['active_jobs']

recipes = [
    ('sharkmode', 'sharkmode-64911bb03be0', '288ba948248c4187ae83b82299641a10364a172335e266fa1579d92104743d3d'),
    ('amv-color', 'amv-color-2e5f73de162d', '14a32759dcf2dfc2e54f19774f2ed34d5ac631d92a69d20313525433becaa27d'),
    ('wrapper-removal', 'wrapper-removal-4acbd9eb44de', '975a88664e9bfab5474ce06a2656f691a257ce2ffeff787541f79e3e48859499'),
]
candidates = {}
evidence_dirs = {}
for case, directory, expected_manifest in recipes:
    evidence = NATIVE / 'accepted' / directory / 'integration-evidence'
    assert sha(evidence / 'manifest.json') == expected_manifest, case
    manifest = json.loads((evidence / 'manifest.json').read_bytes())
    for name, expected in manifest['members'].items():
        path = evidence / name
        assert path.resolve().is_relative_to(evidence.resolve())
        assert path.stat().st_size == expected['bytes'] and sha(path) == expected['sha256'], path
        if path.suffix == '.zip':
            with zipfile.ZipFile(path) as archive:
                assert archive.testzip() is None, path
    candidates[case] = dict(manifest['archive'])
    candidates[case]['integration_manifest_sha256'] = expected_manifest
    evidence_dirs[case] = evidence

retained = json.loads((NATIVE / 'retained-accepted-references.json').read_bytes())['pernicious-deed']
assert retained['capture_binary_sha256'] == '1780c9e517994285775fa75c98c1975c601be0f94c4ad1a376cab16bd8684e8e'
candidates['pernicious-deed'] = {
    'path': retained['archive'], 'sha256': retained['sha256'], 'bytes': retained['bytes'],
    'decoded_sha256': '6edb175e95df37bc926956e9593aa8f95450a74e413e6e43f7fcaad96da0974a',
    'decoded_bytes': 1990339584, 'source_commit': retained['source_commit'],
    'accepted_report_sha256': retained['replay_report_sha256'],
    'runner_sha256': retained['runner_sha256'],
    'capture_binary_sha256': retained['capture_binary_sha256'],
}
deed_evidence = NATIVE / 'retained-reference-evidence.zip'
assert sha(deed_evidence) == '5206e9491557a8a4879c2ec49f5c9b4e6038c0036293dcd2ca8d92227d4bfe75'
with zipfile.ZipFile(deed_evidence) as archive:
    assert archive.testzip() is None

for case, item in candidates.items():
    path = Path(item['path'])
    assert path.name == item['sha256'] + '.tar.zst'
    assert path.stat().st_size == item['bytes'] and sha(path) == item['sha256'], case
    assert not (STORE / path.name).exists(), 'never overwrite a prior archive'
    digest = hashlib.sha256()
    count = 0
    with path.open('rb') as packed, zstandard.ZstdDecompressor().stream_reader(packed) as decoded:
        while block := decoded.read(1024 * 1024):
            digest.update(block)
            count += len(block)
    assert count == item['decoded_bytes'] and digest.hexdigest() == item['decoded_sha256'], case
    print(json.dumps({'case': case, 'compressed_and_decoded_identity_verified': True}), flush=True)

OUT.mkdir()
for case, item in candidates.items():
    path = Path(item['path'])
    target = STORE / path.name
    shutil.copy2(path, target)
    assert target.stat().st_size == item['bytes'] and sha(target) == item['sha256']
    item['fixture_archive'] = 'full_song_lua/' + path.name
for case, evidence in evidence_dirs.items():
    shutil.copytree(evidence, OUT / case)
deed_out = OUT / 'pernicious-deed'
deed_out.mkdir()
for path in sorted(NATIVE.glob('retained-reference-evidence*')):
    if path.is_file():
        shutil.copy2(path, deed_out / path.name)
for name in ('retained-accepted-references.json', 'retained-archive-verification.json'):
    shutil.copy2(NATIVE / name, deed_out / name)
shutil.copy2(release_path, OUT / release_path.name)
shutil.copy2(Path(__file__), OUT / Path(__file__).name)
members = {p.relative_to(OUT).as_posix(): {'bytes': p.stat().st_size, 'sha256': sha(p)}
           for p in sorted(OUT.rglob('*')) if p.is_file()}
manifest = {'created_at': dt.datetime.now(dt.timezone.utc).isoformat(),
            'source_commit': SOURCE_COMMIT, 'fixture_base_commit': git('rev-parse', 'HEAD'),
            'archives': candidates, 'members': members,
            'original_accepted_reports_preserved': True,
            'final_current_build_checkpoint': '../current-main-after07',
            'compressed_and_decoded_bytes_verified_before_copy': True}
(OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
(OUT / 'README.md').write_text(
    '# Accepted native references\n\n'
    'These four archives retain exact native captures from the latest harness binary\n'
    '`1780c9e517994285775fa75c98c1975c601be0f94c4ad1a376cab16bd8684e8e`,\n'
    'built from harness commit `b2af4f355d827fb0e89aead84b4c75a9b8cccf6c`.\n'
    'Sharkmode, AMV colors and wrapper removal were freshly captured in this follow-up.\n'
    'Pernicious Deed preserves the already captured current-harness compressed bytes.\n\n'
    'Each original acceptance/pack receipt retains its actual source commit and\n'
    'runner identity. The AMV and wrapper packs bind to the final source commit\n'
    '`af6a6c9e045f5dfb13abe38bd4eb58d7326f2e26`. The final common-build replay\n'
    'outcomes and full remaining coverage are in `../current-main-after07`.\n'
    'Earlier acceptance receipts have not been relabeled as final-build results.\n\n'
    'Compressed hashes, complete decoded hashes and byte counts were independently\n'
    'checked before copying. The repository split manifest records the archive\n'
    'parts; no existing archive was replaced. Native and accepted-replay evidence,\n'
    'resource limits, source bindings and guest release custody remain alongside\n'
    'each archive. Acceptance does not establish whole-song, application-build or\n'
    'framebuffer-pixel parity.\n', encoding='utf-8')
print(json.dumps({'evidence': str(OUT), 'archives': {k: v['fixture_archive'] for k, v in candidates.items()},
                  'member_count': len(members), 'manifest_sha256': sha(OUT/'manifest.json')}), flush=True)
