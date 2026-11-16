import datetime, hashlib, json, os, pathlib, re, shutil, subprocess

ROOT = pathlib.Path('/opt/song-lua-audit')
REPO = ROOT / 'input-deadsync'
OUT = ROOT / 'pass3-score-redraw-build-final'
assert not OUT.exists()
OUT.mkdir()

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

audit = json.loads((ROOT / 'pass3-score-redraw-compat-audit/audit.json').read_text())
assert 'finished_at' in audit and audit['candidate_files_restored']
assert all(item['exit'] == 101 for item in audit['checks'].values())
before = (ROOT / 'pass3-score-redraw-compat-audit/before-score-fix.log').read_text()
after = (ROOT / 'pass3-score-redraw-compat-audit/candidate-compat.log').read_text()
assert re.search(r'actual:.*\nexpected:.*', before).group() == re.search(r'actual:.*\nexpected:.*', after).group()
assert '16 passed; 1 failed' in after
previous = json.loads((ROOT / 'pass3-score-redraw-build-format/source-proof.json').read_text())
for name, expected in previous['source_normalized_sha256'].items():
    assert sha(REPO / name) == expected, name
files = json.loads((ROOT / 'score-redraw-final-text.json').read_text())
for name, item in files.items():
    assert sha(REPO / name) == item['before_sha256'], name
for name, item in files.items():
    (REPO / name).write_text(item['text'])
    assert sha(REPO / name) == item['after_sha256']
proof = {'base_runner': previous, 'source_normalized_sha256': previous['source_normalized_sha256'] |
         {name: item['after_sha256'] for name, item in files.items()}, 'started_at': now(),
         'compatibility_baseline_audit': audit, 'checks': {}}
(OUT / 'source-proof.json').write_text(json.dumps(proof, indent=2) + '\n')
env = dict(os.environ, PATH='/home/parity/.cargo/bin:' + os.environ['PATH'],
           CARGO_TARGET_DIR=str(ROOT / 'deadsync/target'), CARGO_PROFILE_RELEASE_LTO='false',
           CARGO_PROFILE_RELEASE_CODEGEN_UNITS='16', CARGO_PROFILE_RELEASE_DEBUG='1',
           CARGO_PROFILE_RELEASE_STRIP='none', RUSTFLAGS='-C force-frame-pointers=yes')
checks = [
    ('compat-tests', ['cargo', 'test', '--locked', '--release', '-j', '6', '-p', 'deadsync-song-lua',
                     '--features', 'test-support', '--test', 'compat_globals', '--', '--nocapture']),
    ('score-tests', ['cargo', 'test', '--locked', '--release', '-j', '6', '-p', 'deadsync-song-lua',
                    '--features', 'test-support', '--test', 'gameplay_score', '--', '--nocapture']),
    ('native-gameplay-tests', ['cargo', 'test', '--locked', '--release', '-j', '6', '--test',
                               'song_lua_itgmania_semantic_parity', 'native_gameplay::', '--', '--test-threads=2']),
]
for label, args in checks:
    print(label, flush=True)
    started = now()
    with (OUT / (label + '.log')).open('w') as log:
        result = subprocess.run(args, cwd=REPO, env=env, stdout=log, stderr=subprocess.STDOUT)
    proof['checks'][label] = {'command': args, 'exit': result.returncode, 'started_at': started, 'finished_at': now()}
    text = (OUT / (label + '.log')).read_text()
    if label == 'compat-tests':
        assert result.returncode == 101 and '16 passed; 1 failed' in text
        assert re.search(r'actual:.*\nexpected:.*', text).group() == re.search(r'actual:.*\nexpected:.*', before).group()
        proof['known_unrelated_compatibility_failure'] = 'SecondsToMSSMsMs(infinity): identical before/after release result, frozen expectation differs'
    else:
        assert result.returncode == 0, label
    (OUT / 'validation.json').write_text(json.dumps(proof, indent=2) + '\n')
with (OUT / 'build-artifacts.jsonl').open('w') as log:
    subprocess.run(['cargo', 'rustc', '--locked', '--release', '--test', 'full_song_lua', '-j', '6',
                    '--message-format=json-render-diagnostics'], cwd=REPO, env=env, stdout=log, check=True)
rows = [json.loads(line) for line in (OUT / 'build-artifacts.jsonl').read_text().splitlines() if line.startswith('{')]
binary = next(r['executable'] for r in rows if r.get('target', {}).get('name') == 'full_song_lua' and r.get('executable'))
runner = ROOT / 'bin/full_song_lua-pass3-score-redraw-final'
shutil.copy2(binary, runner)
for name, digest in proof['source_normalized_sha256'].items():
    assert sha(REPO / name) == digest, name
proof.update(finished_at=now(), runner_sha256=sha(runner))
(OUT / 'build-proof.json').write_text(json.dumps(proof, indent=2) + '\n')
print(json.dumps({'runner_sha256': proof['runner_sha256']}), flush=True)
