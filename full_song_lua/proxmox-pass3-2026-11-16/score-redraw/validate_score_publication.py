import datetime, hashlib, json, pathlib, re, subprocess
from urllib.parse import unquote
import zstandard

WORK = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path('C:/GitHub/deadsync')
REPO = ROOT / 'tests/fixtures'
STORE = REPO / 'full_song_lua'
REPORT = STORE / 'proxmox-pass3-2026-11-16'
SCORE = REPORT / 'score-redraw'

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def old(name):
    return json.loads(subprocess.check_output(['git', '-C', str(REPO), 'show', 'f89bb0f0088c3b0cdc31accff2d0c6e05b561e8f:full_song_lua/' + name]))

catalog = {r['archive']: r for r in read(STORE / 'committed-songs.json')}
previous = {r['archive']: r for r in old('committed-songs.json')}
assert all(catalog[k] == v for k, v in previous.items())
added = set(catalog) - set(previous)
assert len(previous) == 1008 and len(catalog) == 1011 and len(added) == 3
assert (STORE / 'committed-archives.txt').read_text().splitlines() == sorted(catalog)
split = {r['archive']: r for r in read(STORE / 'split-archives.json')['archives']}
oldsplit = {r['archive']: r for r in old('split-archives.json')['archives']}
assert all(split[k] == v for k, v in oldsplit.items())
published = {r['archive']: r for r in read(REPORT / 'published-archives.json')}
archives = []
for name in sorted(added):
    e = split[name]
    digest = hashlib.sha256()
    for part in e['parts']:
        p = STORE / part['file']
        assert p.stat().st_size == part['bytes'] < 50_000_000 and sha(p) == part['sha256']
        with p.open('rb') as stream:
            while block := stream.read(4 * 1024 * 1024):
                digest.update(block)
    assert digest.hexdigest() == e['sha256'] == name.removesuffix('.tar.zst')
    assert sum(p['bytes'] for p in e['parts']) == e['bytes'] == published[name]['bytes']
    archive = pathlib.Path('D:/deadsync-lua-pass3-20261116/score-archives') / name
    assert sha(archive) == e['sha256']
    with archive.open('rb') as stream, zstandard.ZstdDecompressor().stream_reader(stream) as raw:
        raw_hash = hashlib.file_digest(raw, 'sha256').hexdigest()
    assert raw_hash == published[name]['uncompressed_sha256']
    archives.append({'archive': name, 'bytes': e['bytes'], 'parts': len(e['parts'])})

evidence = read(SCORE / 'evidence.json')
for item in evidence:
    p = SCORE / item['local']
    assert p.stat().st_size == item['bytes'] and sha(p) == item['sha256'], item['local']
proof = read(SCORE / 'pass3-score-redraw-build-final/build-proof.json')
commit = read(SCORE / 'score-code-commit.json')['commit']
for name, digest in proof['source_normalized_sha256'].items():
    raw = subprocess.check_output(['git', '-C', str(ROOT), 'show', commit + ':' + name])
    assert hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest() == digest, name
oracle = read(SCORE / 'pass3-score-harness-final/build-proof.json')
for name, digest in oracle['tracked_source_sha256'].items():
    raw = subprocess.check_output(['git', '-C', 'C:/GitHub/itgmania-harness', 'show', oracle['harness_commit'] + ':' + name])
    assert hashlib.sha256(raw).hexdigest() == digest, name
for name, digest in oracle['theme_changed_source_sha256'].items():
    raw = subprocess.check_output(['git', '-C', 'C:/GitHub/itgmania-harness/vendor/simply-love', 'show', oracle['theme_commit'] + ':' + name])
    assert hashlib.sha256(raw).hexdigest() == digest, name
    if name != 'BGAnimations/ScreenGameplay underlay/default.lua':
        ds = subprocess.check_output(['git', '-C', str(ROOT), 'show', commit + ':crates/deadsync-song-lua/assets/simply-love/' + name])
        assert ds == raw

replays = []
for folder in ['pass3-score-final-controls', 'pass3-score-regressions']:
    for p in sorted((SCORE / folder).glob('*/result.json')):
        result = read(p)
        assert result['status'] == 'pass'
        with (p.parent / 'report.json.zst').open('rb') as stream, zstandard.ZstdDecompressor().stream_reader(stream) as raw:
            report = json.load(raw)
        assert report['archive_accepted'] and report['capture_completed_gameplay']
        assert report['native_frames'] == report['replayed_frames'] > 0
        assert not report['mismatches'] and not report['errors'] and report['broadcast_params_compared']
        q = report['command_queries']
        assert q['compared'] and q['native_count'] == q['actual_count']
        if folder == 'pass3-score-final-controls':
            with (p.parent / 'trace/native.json.zst').open('rb') as stream, zstandard.ZstdDecompressor().stream_reader(stream) as raw:
                native = json.load(raw)
            assert native['harness_version'] == '0.1.104' and not native['script_errors']
            assert all(v == 0 for k, v in native.items() if k.startswith('dropped_'))
            assert len(result['samples']) == {'score-format': 16, 'score-queue-v2': 1, 'score-redraw-manual': 3}[result['id']]
        replays.append({'id': result['id'], 'frames': report['replayed_frames'], 'queries': q['actual_count']})
assert len(replays) == 13
for folder, name, expected in [('pass3-score-redraw-build-final', 'score-tests.log', (1, 0, 0)),
                               ('pass3-score-redraw-build-final', 'native-gameplay-tests.log', (77, 0, 0)),
                               ('pass3-score-harness-final', 'unit-tests.log', (215, 0, 5))]:
    text = (SCORE / folder / name).read_text(encoding='utf-8')
    matches = re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;', text)
    assert len(matches) == 1 and tuple(map(int, matches[0])) == expected
before = (SCORE / 'pass3-score-redraw-compat-audit/before-score-fix.log').read_text(encoding='utf-8')
after = (SCORE / 'pass3-score-redraw-build-final/compat-tests.log').read_text(encoding='utf-8')
assert '16 passed; 1 failed' in after
assert re.search(r'actual:.*\nexpected:.*', before).group() == re.search(r'actual:.*\nexpected:.*', after).group()
snap = read(SCORE / 'score-format-snapshot-update.json')
assert sha(REPO / 'regression-expectations/deadsync-song-lua/506d3279b33b4ad7.snap') == snap['after_sha256']
raw = subprocess.check_output(['git', '-C', str(REPO), 'show', 'f89bb0f0088c3b0cdc31accff2d0c6e05b561e8f:regression-expectations/deadsync-song-lua/506d3279b33b4ad7.snap'])
assert hashlib.sha256(raw).hexdigest() == snap['before_sha256']

ledger = read(REPORT / 'case-ledger.json')
assert len(ledger) == 503 and sum(r['status'] == 'pass' for r in ledger) == 489
assert ledger == old('proxmox-pass3-2026-11-16/case-ledger.json')
guide = (STORE / 'fixture-runtimes.md').read_text(encoding='utf-8')
primary = guide[guide.index('## Known failures:'):guide.index('## Supplemental profiles and controls')] + guide[guide.index('## Complete passing primary lookup'):guide.index('## Sources and refresh method')]
ids = re.findall(r'(?m)^\|.*\| ([0-9a-f]{16}) \|$', primary)
assert len(ids) == len(set(ids)) == 503 and set(ids) == {r['id'] for r in ledger}
link_count = 0
for path in [STORE / 'fixture-runtimes.md', REPORT / 'README.md', SCORE / 'README.md']:
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
           'source_files_verified': len(proof['source_normalized_sha256']), 'harness_files_verified': len(oracle['tracked_source_sha256']),
           'retained_artifacts_verified': len(evidence), 'new_archives': archives, 'complete_catalog_archives': len(catalog),
           'full_replays': replays, 'primary_passes': 489, 'primary_nonpasses': 14, 'all_chart_gate_satisfied': False,
           'local_markdown_links_verified': link_count, 'runtime_guide_primary_ids': len(ids), 'protected_user_diff_sha256': user_hash}
(SCORE / 'publication-validation.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
print(json.dumps(summary, indent=2))
