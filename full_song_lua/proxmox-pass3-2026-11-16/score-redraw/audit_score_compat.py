import base64, datetime, hashlib, json, os, pathlib, subprocess

ROOT = pathlib.Path('/opt/song-lua-audit')
REPO = ROOT / 'input-deadsync'
OUT = ROOT / 'pass3-score-redraw-compat-audit'
assert not OUT.exists()
OUT.mkdir()
bundle = json.loads((ROOT / 'score-compat-audit-input.json').read_text())

def sha(data):
    return hashlib.sha256(data).hexdigest()

def write(name, data):
    path = REPO / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

env = dict(os.environ, PATH='/home/parity/.cargo/bin:' + os.environ['PATH'],
           CARGO_TARGET_DIR=str(ROOT / 'deadsync/target'), CARGO_PROFILE_RELEASE_LTO='false',
           CARGO_PROFILE_RELEASE_CODEGEN_UNITS='16', CARGO_PROFILE_RELEASE_DEBUG='1',
           CARGO_PROFILE_RELEASE_STRIP='none', RUSTFLAGS='-C force-frame-pointers=yes')
proof = {'started_at': now(), 'baseline_revisions': bundle['baseline_revisions'], 'files': {}, 'checks': {}}
saved = {}
for name, item in bundle['baseline'].items():
    current = (REPO / name).read_bytes()
    assert sha(current) == item['candidate_sha256'], name
    saved[name] = current
    baseline = base64.b64decode(item['baseline_base64'])
    proof['files'][name] = {'candidate_sha256': sha(current), 'baseline_sha256': sha(baseline)}
for name, item in bundle['restore_missing'].items():
    path = REPO / name
    data = base64.b64decode(item['base64'])
    assert sha(data) == item['sha256']
    assert not path.exists(), name
    write(name, data)
    proof.setdefault('restored_missing', {})[name] = sha(data)

def check(label, extra):
    args = ['cargo', 'test', '--locked', '--release', '-j', '6', '-p', 'deadsync-song-lua',
            '--features', 'test-support', '--test', 'compat_globals'] + extra + ['--', '--nocapture']
    started = now()
    with (OUT / (label + '.log')).open('w') as log:
        result = subprocess.run(args, cwd=REPO, env=env, stdout=log, stderr=subprocess.STDOUT)
    proof['checks'][label] = {'command': args, 'exit': result.returncode, 'started_at': started, 'finished_at': now()}
    (OUT / 'audit.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(label, result.returncode, flush=True)

try:
    for name, item in bundle['baseline'].items():
        write(name, base64.b64decode(item['baseline_base64']))
    check('before-score-fix', ['formatting_and_numeric_helpers_match_existing_argument_conversion'])
finally:
    for name, data in saved.items():
        write(name, data)
        assert (REPO / name).read_bytes() == data
    proof['candidate_files_restored'] = True
    (OUT / 'audit.json').write_text(json.dumps(proof, indent=2) + '\n')
check('candidate-compat', [])
proof['finished_at'] = now()
(OUT / 'audit.json').write_text(json.dumps(proof, indent=2) + '\n')
