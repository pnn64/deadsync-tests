"""Publish the three fully compared 0.1.104 score controls, preserving old entries."""
import hashlib, json, pathlib, shutil, tarfile
import zstandard

WORK = pathlib.Path(__file__).resolve().parent
STORE = pathlib.Path('C:/GitHub/deadsync/tests/fixtures/full_song_lua')
REPORT = STORE / 'proxmox-pass3-2026-11-16'
EVIDENCE = WORK / 'score-redraw-collected'
DOWNLOADS = pathlib.Path('D:/deadsync-lua-pass3-20261116/score-archives')

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

catalog = {r['archive']: r for r in read(STORE / 'committed-songs.json')}
split = {r['archive']: r for r in read(STORE / 'split-archives.json')['archives']}
published = read(REPORT / 'published-archives.json')
known = {r['archive'] for r in published}
added = []
for ident in ['score-queue-v2', 'score-redraw-manual', 'score-format']:
    result_path = EVIDENCE / 'pass3-score-final-controls' / ident / 'result.json'
    result = read(result_path)
    assert result['status'] == 'pass' and result['native']['harness_version'] == '0.1.104'
    c = result['comparison']
    assert c['archive_accepted'] and c['mismatch_count'] == c['error_count'] == 0
    assert c['native_frames'] == c['replayed_frames'] > 0
    artifact = result['accepted_artifact']
    archive = DOWNLOADS / pathlib.Path(artifact['file']).name
    name = archive.name
    digest = sha(archive)
    assert name == digest + '.tar.zst' and digest == artifact['sha256']
    assert archive.stat().st_size == artifact['bytes']
    with archive.open('rb') as stream, zstandard.ZstdDecompressor().stream_reader(stream) as raw:
        raw_hash = hashlib.file_digest(raw, 'sha256').hexdigest()
    assert raw_hash == artifact['uncompressed_sha256'] == c['fixture_sha256']
    with archive.open('rb') as stream, zstandard.ZstdDecompressor().stream_reader(stream) as raw, tarfile.open(fileobj=raw, mode='r|') as tar:
        member = next(iter(tar))
        assert member.name == 'manifest.json'
        manifest = json.load(tar.extractfile(member))
    assert manifest['harness_version'] == '0.1.104'
    assert manifest['chart']['source_path'] == result['source_simfile']
    if name in known:
        assert name in catalog
        continue
    parts = []
    folder = STORE / 'archive-parts' / digest
    folder.mkdir(parents=True, exist_ok=True)
    with archive.open('rb') as stream:
        while block := stream.read(48_000_000):
            part = folder / f'{len(parts):03}.part'
            if part.exists():
                assert part.read_bytes() == block
            else:
                part.write_bytes(block)
            parts.append({'file': part.relative_to(STORE).as_posix(), 'bytes': len(block), 'sha256': sha(part)})
    assert sum(p['bytes'] for p in parts) == artifact['bytes']
    split[name] = {'archive': name, 'bytes': artifact['bytes'], 'sha256': digest, 'parts': parts}
    catalog[name] = {'title': manifest['chart']['title'], 'source_simfile': manifest['chart']['source_path'],
                     'harness_version': manifest['harness_version'], 'archive': name}
    published.append({'id': ident, 'harness_version': '0.1.104', 'archive': name, 'bytes': artifact['bytes'],
                      'sha256': digest, 'uncompressed_sha256': raw_hash, 'source_simfile': result['source_simfile'],
                      'source_snapshot': result['source_snapshot'], 'local_evidence': result_path.relative_to(WORK).as_posix(),
                      'acceptance_basis': c['acceptance_basis'], 'production_parity_proven': c['production_parity_proven']})
    known.add(name)
    added.append({'id': ident, 'archive': name, 'bytes': artifact['bytes'], 'parts': len(parts)})
write(REPORT / 'published-archives.json', published)
write(STORE / 'committed-songs.json', [catalog[name] for name in sorted(catalog)])
write(STORE / 'split-archives.json', {'version': 1, 'archives': [split[name] for name in sorted(split)]})
(STORE / 'committed-archives.txt').write_text('\n'.join(sorted(catalog)) + '\n', encoding='utf-8')
ignore = STORE.parent / '.gitignore'
marker = '# Restored split archives (managed by prepare_test_fixtures.py)'
before = ignore.read_text(encoding='utf-8').split(marker)[0].rstrip()
ignore.write_text(before + '\n\n' + marker + '\n/full_song_lua/.fixture-*\n' +
                  '\n'.join('/full_song_lua/' + name for name in sorted(split)) + '\n', encoding='utf-8')
write(WORK / 'score-archives-publication.json', {'added': added, 'complete_catalog_archives': len(catalog)})
print(json.dumps({'added': added, 'complete_catalog_archives': len(catalog)}))
