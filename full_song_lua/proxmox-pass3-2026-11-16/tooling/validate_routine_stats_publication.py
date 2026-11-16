import collections, datetime, hashlib, json, pathlib, re, subprocess
from urllib.parse import unquote
import zstandard

WORK = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path('C:/GitHub/deadsync')
REPO = ROOT / 'tests/fixtures'
STORE = REPO / 'full_song_lua'
REPORT = STORE / 'proxmox-pass3-2026-11-16'

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def old(name):
    return json.loads(subprocess.check_output(['git', '-C', str(REPO), 'show', 'HEAD:full_song_lua/' + name]))

catalog = {r['archive']: r for r in read(STORE / 'committed-songs.json')}
previous = {r['archive']: r for r in old('committed-songs.json')}
assert all(catalog[k] == v for k, v in previous.items())
added = set(catalog) - set(previous)
assert len(previous) == 1004 and len(catalog) == 1008 and len(added) == 4
assert (STORE / 'committed-archives.txt').read_text().splitlines() == sorted(catalog)
split = {r['archive']: r for r in read(STORE / 'split-archives.json')['archives']}
oldsplit = {r['archive']: r for r in old('split-archives.json')['archives']}
assert all(split[k] == v for k, v in oldsplit.items())
published = {r['archive']: r for r in read(REPORT / 'published-archives.json')}
new_archives = []
for name in sorted(added):
    item = split[name]
    digest = hashlib.sha256()
    for part in item['parts']:
        path = STORE / part['file']
        assert path.stat().st_size == part['bytes'] < 50_000_000
        assert sha(path) == part['sha256']
        with path.open('rb') as stream:
            while chunk := stream.read(4 * 1024 * 1024):
                digest.update(chunk)
    assert sum(p['bytes'] for p in item['parts']) == item['bytes'] == published[name]['bytes']
    assert digest.hexdigest() == item['sha256'] == name.removesuffix('.tar.zst')
    source = WORK / published[name]['local_evidence']
    compressed = source.parent / 'accepted' / name
    assert sha(compressed) == item['sha256']
    with compressed.open('rb') as stream, zstandard.ZstdDecompressor().stream_reader(stream) as raw:
        uncompressed_sha = hashlib.file_digest(raw, 'sha256').hexdigest()
    assert uncompressed_sha == published[name]['uncompressed_sha256'] == read(source)['comparison']['fixture_sha256']
    new_archives.append({'archive': name, 'bytes': item['bytes'], 'parts': len(item['parts'])})

evidence = read(REPORT / 'routine-stats-evidence.json')
for item in evidence:
    path = REPORT / item['target'] if item['target'] else WORK / 'collected/1402' / item['local']
    assert path.stat().st_size == item['bytes'] and sha(path) == item['sha256'], str(path)
proof = read(REPORT / 'native-validation/pass3-routine-stats-observers-resume/build-proof.json')
commit = read(WORK / 'routine-stats-code-commit.json')['commit']
for name, digest in proof['source_normalized_sha256'].items():
    raw = subprocess.check_output(['git', '-C', str(ROOT), 'show', commit + ':' + name])
    assert hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest() == digest, name

replays = []
for path in sorted((REPORT / 'routine-stats-replays').glob('*/result.json')):
    result = read(path)
    assert result['status'] == 'pass'
    with (path.parent / 'report.json.zst').open('rb') as stream, zstandard.ZstdDecompressor().stream_reader(stream) as raw:
        report = json.load(raw)
    assert report['archive_accepted'] and report['capture_completed_gameplay']
    assert report['native_frames'] == report['replayed_frames'] > 0
    assert not report['mismatches'] and not report['errors']
    assert report['broadcast_params_compared']
    queries = report['command_queries']
    assert queries['compared'] and queries['native_count'] == queries['actual_count']
    replays.append({'id': result['id'], 'frames': report['replayed_frames'], 'queries': queries['actual_count']})
assert len(replays) == 10
ledger = read(REPORT / 'case-ledger.json')
assert len(ledger) == 503 and sum(r['status'] == 'pass' for r in ledger) == 489
before = old('proxmox-pass3-2026-11-16/case-ledger.json')
assert {r['id']: r['status'] for r in before} == {r['id']: r['status'] for r in ledger}
guide = (STORE / 'fixture-runtimes.md').read_text(encoding='utf-8')
primary_tables = guide[guide.index('## Known failures:'):guide.index('## Supplemental profiles and controls')] + guide[guide.index('## Complete passing primary lookup'):guide.index('## Sources and refresh method')]
ids = re.findall(r'(?m)^\|.*\| ([0-9a-f]{16}) \|$', primary_tables)
assert len(ids) == len(set(ids)) == 503 and set(ids) == {r['id'] for r in ledger}
markdown = [STORE / 'fixture-runtimes.md', REPORT / 'README.md', REPORT / 'routine-stats-replays/README.md', REPORT / 'routine-fail-controls/README.md']
link_count = 0
for path in markdown:
    for link in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
        if link.startswith(('#', 'http://', 'https://')):
            continue
        assert (path.parent / unquote(link.split('#')[0])).exists(), (path, link)
        link_count += 1
protected = ['crates/deadsync-song-lua/src/actors.rs'] + ['crates/deadsync-song-lua/src/actors/' + p for p in ['function_capture.rs', 'lifecycle.rs', 'messages/capture.rs', 'offline.rs', 'song_capture.rs', 'song_replay.rs']]
user_hash = hashlib.sha256(subprocess.check_output(['git', '-C', str(ROOT), 'diff', '--binary', '--', *protected])).hexdigest()
assert user_hash == 'f362069247b6129a8a3a035c439fcbf77fd89c878feae29ee22c02d5475166c0'
subprocess.run(['git', '-C', str(REPO), 'diff', '--check'], check=True, capture_output=True)
summary = {'recorded_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'deadsync_commit': commit,
           'source_files_verified': len(proof['source_normalized_sha256']), 'runner_sha256': proof['runner_sha256'],
           'retained_artifacts_verified': len(evidence), 'new_archives': new_archives,
           'complete_catalog_archives': len(catalog), 'full_replays': replays, 'primary_passes': 489, 'primary_nonpasses': 14,
           'all_chart_gate_satisfied': False, 'local_markdown_links_verified': link_count, 'runtime_guide_primary_ids': len(ids),
           'protected_user_diff_sha256': user_hash}
(REPORT / 'routine-stats-publication-validation.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
print(json.dumps(summary, indent=2))
