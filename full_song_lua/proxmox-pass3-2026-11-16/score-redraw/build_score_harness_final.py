import base64, datetime, hashlib, json, os, pathlib, shutil, subprocess

ROOT = pathlib.Path('/opt/song-lua-audit')
OUT = ROOT / 'pass3-score-harness-final'
assert not OUT.exists()
OUT.mkdir()
harness = ROOT / 'routine-harness'
theme = ROOT / 'routine-theme'
native = ROOT / 'routine-native'
bundle = json.loads((ROOT / 'score-harness-final-input.json').read_text())

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

for name, item in bundle['replacements'].items():
    assert sha(harness / name) == item['before_sha256'], name
    (OUT / ('before-' + name.replace('/', '_'))).write_bytes((harness / name).read_bytes())
for name, digest in bundle['tracked_source_sha256'].items():
    if name not in bundle['replacements']:
        assert sha(harness / name) == digest, name
for name, item in bundle['replacements'].items():
    (harness / name).write_text(item['text'])
for name, digest in bundle['tracked_source_sha256'].items():
    assert sha(harness / name) == digest, name

theme_bundle = OUT / 'score-redraw-theme.bundle'
theme_bundle.write_bytes(base64.b64decode(bundle['theme_bundle_base64']))
subprocess.run(['git', '-C', str(theme), 'fetch', str(theme_bundle), 'HEAD'], check=True)
assert subprocess.check_output(['git', '-C', str(theme), 'rev-parse', 'FETCH_HEAD'], text=True).strip() == bundle['theme_commit']
theme_changes = json.loads((ROOT / 'score-redraw-theme-v2.json').read_text())['files']
for name, item in theme_changes.items():
    assert sha(theme / name) == item['after_sha256'], name
    committed = subprocess.check_output(['git', '-C', str(theme), 'show', bundle['theme_commit'] + ':' + name])
    assert committed == (theme / name).read_bytes(), name
subprocess.run(['git', '-C', str(theme), 'add', '--'] + list(theme_changes), check=True)
subprocess.run(['git', '-C', str(theme), 'checkout', '--detach', bundle['theme_commit']], check=True)
assert not subprocess.check_output(['git', '-C', str(theme), 'status', '--porcelain'], text=True).strip()
previous = json.loads((ROOT / 'pass3-input-clocks/build-proof.json').read_text())
assert sha(native / 'ITGmania-harness-trace') == previous['native_binary_sha256']
proof = {'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'harness_commit': bundle['harness_commit'], 'harness_version': '0.1.104',
         'theme_commit': bundle['theme_commit'], 'native_commit': '663525dcb86eb570d0ef6a2e209678436660ae26',
         'native_binary_sha256': previous['native_binary_sha256'], 'native_build_provenance': previous,
         'tracked_source_sha256': bundle['tracked_source_sha256'],
         'theme_changed_source_sha256': {name: sha(theme / name) for name in theme_changes},
         'worker_checkout_note': 'Harness tracked files match committed source; .gitmodules and vendor symlinks are worker-only dependency routing.'}
(OUT / 'source-proof.json').write_text(json.dumps(proof, indent=2) + '\n')
env = dict(os.environ, PATH='/home/parity/.cargo/bin:' + os.environ['PATH'],
           CARGO_TARGET_DIR=str(ROOT / 'harness/target'), CARGO_PROFILE_RELEASE_LTO='false',
           CARGO_PROFILE_RELEASE_CODEGEN_UNITS='16', ITGMANIA_HARNESS_TRACE_BIN=str(native / 'ITGmania-harness-trace'))
for name, args in [
    ('unit-tests', ['cargo', 'test', '--locked', '--release', '-j', '2', '--bin', 'itgmania-harness-rs']),
    ('harness-build', ['cargo', 'build', '--locked', '--release', '-j', '2']),
]:
    print(name, flush=True)
    with (OUT / (name + '.log')).open('w') as log:
        subprocess.run(args, cwd=harness, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
runner = ROOT / 'bin/itgmania-harness-pass3-score-redraw'
shutil.copy2(ROOT / 'harness/target/release/itgmania-harness-rs', runner)
proof.update(finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(), harness_binary_sha256=sha(runner))
(OUT / 'build-proof.json').write_text(json.dumps(proof, indent=2) + '\n')
print(json.dumps({'harness_binary_sha256': proof['harness_binary_sha256'], 'version': '0.1.104'}), flush=True)
