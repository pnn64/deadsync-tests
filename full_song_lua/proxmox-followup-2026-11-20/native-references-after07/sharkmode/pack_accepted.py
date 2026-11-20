"""Prepare exact acceptance gates, pack one case, and verify its download.

Preparation is local only. Packing must be invoked separately after the parent
reviews acceptance. All outputs are exclusive creations; there is no retry.
"""
import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import zipfile
import zstandard
import remote_capture

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[2]
RECIPES = json.loads((ROOT / 'pack-recipes.json').read_bytes())

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def write(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')

def prepare(args):
    recipe = RECIPES['cases'][args.case]
    candidate = Path(recipe['local_candidate'])
    assert candidate.name == recipe['sha256'] + '.tar'
    assert candidate.stat().st_size == recipe['bytes'] and sha(candidate) == recipe['sha256']
    report_path = Path(args.replay_directory) / 'report.json'
    execution_path = Path(args.replay_directory) / 'execution.json'
    assert sha(report_path) == args.report_sha256
    assert sha(execution_path) == args.execution_sha256
    report = json.loads(report_path.read_bytes())
    execution = json.loads(execution_path.read_bytes())
    assert report['fixture_sha256'] == execution['archive_sha256'] == recipe['sha256']
    assert execution['archive_bytes'] == recipe['bytes'] and execution['exit_code'] == 0
    assert report['archive_accepted'] is True
    assert report['execution_path'] == 'production-and-diagnostic-live-lua'
    assert report['diagnostic_replay_checks_passed'] is True
    assert report['production_gameplay_checks_passed'] is True
    assert report['production_preparation_exercised'] is True
    assert report['capture_completed_gameplay'] is True
    assert report['errors'] == [] and report['mismatches'] == []
    assert execution['binary_sha256'] == args.runner_sha256
    runner = Path(execution['command'][0])
    assert sha(runner) == args.runner_sha256
    binding_path = Path(args.build_binding)
    assert sha(binding_path) == execution['compiled_build_binding_sha256']
    binding = json.loads(binding_path.read_bytes())
    assert binding == execution['compiled_build_binding']
    assert binding['binaries']['full_song_lua']['sha256'] == args.runner_sha256
    assert binding['cargo_build_jsonl_sha256'] == execution['cargo_build_jsonl_sha256']
    compiled = binding['source_identity']['source_files']
    source_commit = subprocess.run(['git', 'rev-parse', args.source_commit], cwd=PROJECT,
        capture_output=True, check=True).stdout.decode().strip()
    source_proofs = {}
    for path, expected in compiled.items():
        raw = subprocess.run(['git', 'show', source_commit + ':' + path], cwd=PROJECT,
            capture_output=True, check=True).stdout
        variants = [('as_committed', raw), ('crlf', raw.replace(b'\n', b'\r\n'))]
        matches = [name for name, value in variants if hashlib.sha256(value).hexdigest() == expected]
        assert matches, 'compiled source does not match commit: ' + path
        source_proofs[path] = {'compiled_sha256': expected, 'committed_sha256': hashlib.sha256(raw).hexdigest(),
            'matching_line_endings': matches}
    native_evidence = Path(recipe['native_evidence'])
    assert sha(native_evidence) == recipe['native_evidence_sha256']
    with zipfile.ZipFile(native_evidence) as archive:
        assert archive.testzip() is None
        summary = json.loads(archive.read('native-summary.json'))
    assert summary.get('harness_revision', summary.get('harness_commit')) == RECIPES['harness_commit']
    assert summary['harness_version'] == '0.1.110'
    assert summary['completion']['reason'] == 'gameplay-exit' and summary['completion']['stage_committed'] is True
    assert all(value == 0 for value in summary['dropped'].values())
    with tarfile.open(candidate, 'r:') as archive:
        manifest = json.load(archive.extractfile('manifest.json'))
    assert manifest['harness_version'] == '0.1.110'
    assert manifest['runtime']['command_observer']['capture_binary_sha256'] == RECIPES['harness_sha256']
    trace = next(row for row in manifest['files'] if row['path'] == manifest['chart']['trace'])
    assert trace['sha256'] == summary['trace_sha256'] and trace['bytes'] == summary['trace_bytes']
    for name, expected in execution['reports'].items():
        path = execution_path.parent / name
        assert path.stat().st_size == expected['bytes'] and sha(path) == expected['sha256']
    destination = ROOT / 'accepted' / (args.case + '-' + args.report_sha256[:12])
    destination.mkdir(parents=True, exist_ok=False)
    proof = {'case': args.case, 'candidate': recipe, 'accepted_report_path': str(report_path),
        'accepted_report_sha256': args.report_sha256, 'execution_path': str(execution_path),
        'execution_sha256': args.execution_sha256, 'runner_path': str(runner), 'runner_sha256': args.runner_sha256,
        'compiled_build_binding_path': str(binding_path), 'compiled_build_binding_sha256': sha(binding_path),
        'source_commit': source_commit, 'compiled_sources': source_proofs,
        'source_identity_at_execution': execution['source_identity'],
        'compiled_source_identity': binding['source_identity'],
        'harness_commit': RECIPES['harness_commit'], 'harness_sha256': RECIPES['harness_sha256'],
        'native_counts': summary['counts'], 'native_trace_sha256': summary['trace_sha256'],
        'archive_accepted': True, 'diagnostic_replay_checks_passed': True, 'production_gameplay_checks_passed': True,
        'pending_coverage_count': len(report['pending_coverage']),
        'parity_claim_flags': {k: v for k, v in report.items() if k.endswith('_parity_proven')},
        'guest_root': RECIPES['guest_parent'] + '/' + destination.name,
        'resource_budget': RECIPES['resources']}
    write(destination / 'acceptance-proof.json', proof)
    helper = (ROOT / 'bounded_stage.py').read_text(encoding='utf-8').replace('deadsync-shark-fresh-', 'deadsync-accepted-')
    with (destination / 'bounded_stage.py').open('x', encoding='utf-8', newline='\n') as output:
        output.write(helper)
    package = destination / 'accepted-replay-evidence.zip'
    with zipfile.ZipFile(package, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name in execution['reports']:
            archive.write(execution_path.parent / name, name)
        archive.write(execution_path, 'execution.json')
        archive.write(binding_path, 'compiled-build-binding.json')
        archive.write(destination / 'acceptance-proof.json', 'acceptance-proof.json')
        archive.write(destination / 'bounded_stage.py', 'bounded_stage.py')
    with zipfile.ZipFile(package) as archive:
        assert archive.testzip() is None
    write(destination / 'prepared.json', {'case': args.case, 'directory': str(destination),
        'package_sha256': sha(package), 'package_bytes': package.stat().st_size,
        'acceptance_proof_sha256': sha(destination / 'acceptance-proof.json'), 'packing_executed': False})
    print(json.dumps({'prepared': True, 'directory': str(destination), 'package_sha256': sha(package)}), flush=True)

def load_prepared(args):
    directory = Path(args.directory).resolve()
    assert directory.is_relative_to(ROOT / 'accepted')
    prepared = json.loads((directory / 'prepared.json').read_bytes())
    proof_path = directory / 'acceptance-proof.json'
    assert sha(proof_path) == prepared['acceptance_proof_sha256']
    proof = json.loads(proof_path.read_bytes())
    package = directory / 'accepted-replay-evidence.zip'
    assert sha(package) == prepared['package_sha256'] and package.stat().st_size == prepared['package_bytes']
    return directory, prepared, proof, package

def pack(args):
    directory, prepared, proof, package = load_prepared(args)
    assert not (directory / 'pack-execution.json').exists()
    guest = """
import base64,fcntl,hashlib,io,json,pathlib,shutil,subprocess,sys,zipfile
root=pathlib.Path(ROOT)
assert not root.exists(), 'exclusive pack directory already exists'
parent=root.parent;parent.mkdir(parents=True,exist_ok=True)
with (parent/'.packing.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert shutil.disk_usage(parent).free>=4*1024**3
 ps=subprocess.run(['ps','-eo','pid,ppid,comm,args'],capture_output=True,text=True,check=True).stdout
 active=[line for line in ps.splitlines() if any(s in line for s in ['ITGmania-harness-trace','itgmania-harness-rs','full_song_lua-','/cargo ','/rustc '])]
 assert not active,active
 raw=base64.b64decode(PAYLOAD);assert hashlib.sha256(raw).hexdigest()==PACKAGE_SHA
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  assert z.testzip() is None
  names=z.namelist();assert len(names)==len(set(names)) and all('/' not in name and '\\\\' not in name for name in names)
  root.mkdir()
  for name in names:
   with (root/name).open('xb') as output:output.write(z.read(name))
 (root/'tmp').mkdir()
 sys.path.insert(0,str(root));import bounded_stage as bounds
 proof=json.loads((root/'acceptance-proof.json').read_bytes())
 candidate=pathlib.Path(proof['candidate']['guest_candidate'])
 assert bounds.digest(candidate)==proof['candidate']['sha256'] and candidate.stat().st_size==proof['candidate']['bytes']
 assert bounds.digest(root/'report.json')==proof['accepted_report_sha256']
 assert bounds.digest(bounds.HARNESS)==proof['harness_sha256']
 profile=json.loads((bounds.PROFILE/'proof/source-proof.json').read_bytes())
 assert profile['pins']['harness']==proof['harness_commit']
 bounds.stage('pack',[bounds.HARNESS,'song-lua-pack',candidate,'--report',root/'report.json','--out',root/'packed'],180)
 outputs=list((root/'packed').glob('*.tar.zst'));assert len(outputs)==1
 output=outputs[0];sha=bounds.digest(output);assert output.name==sha+'.tar.zst'
 assert bounds.digest(candidate)==proof['candidate']['sha256']
 result={'packed':True,'case':proof['case'],'path':str(output),'sha256':sha,'bytes':output.stat().st_size,
  'candidate_sha256':proof['candidate']['sha256'],'report_sha256':proof['accepted_report_sha256'],
  'execution_sha256':proof['execution_sha256'],'source_commit':proof['source_commit'],'runner_sha256':proof['runner_sha256'],
  'harness_sha256':proof['harness_sha256'],'candidate_unchanged':True}
 bounds.write(root/'pack-result.json',result)
 print(json.dumps(result),flush=True)
""".replace('ROOT', repr(proof['guest_root'])).replace('PAYLOAD', repr(base64.b64encode(package.read_bytes()).decode())).replace('PACKAGE_SHA', repr(prepared['package_sha256']))
    started = remote_capture.now()
    result = remote_capture.remote(guest, 240)
    receipt = {'started_at': started, 'finished_at': remote_capture.now(), 'exit': result.returncode,
        'stdout': result.stdout.decode(errors='replace'), 'stderr': result.stderr.decode(errors='replace'),
        'prepared_sha256': sha(directory / 'prepared.json'), 'script_sha256': sha(__file__)}
    write(directory / 'pack-execution.json', receipt)
    print(json.dumps(receipt), flush=True)
    raise SystemExit(result.returncode)

def download(args):
    directory, _, proof, _ = load_prepared(args)
    execution = json.loads((directory / 'pack-execution.json').read_bytes())
    assert execution['exit'] == 0
    result = remote_capture.remote('import pathlib,sys\nsys.stdout.buffer.write(pathlib.Path(' + repr(proof['guest_root'] + '/pack-result.json') + ').read_bytes())\n')
    assert result.returncode == 0, result.stderr.decode(errors='replace')
    packed = json.loads(result.stdout)
    assert packed['candidate_sha256'] == proof['candidate']['sha256'] and packed['report_sha256'] == proof['accepted_report_sha256']
    assert packed['path'] == proof['guest_root'] + '/packed/' + packed['sha256'] + '.tar.zst'
    destination = directory / (packed['sha256'] + '.tar.zst')
    guest = 'import pathlib,shutil,sys\nwith pathlib.Path(' + repr(packed['path']) + ').open("rb") as source:shutil.copyfileobj(source,sys.stdout.buffer,1<<20)\n'
    with destination.open('xb') as output:
        result = remote_capture.remote(guest, 180, output)
    assert result.returncode == 0, result.stderr.decode(errors='replace')
    assert destination.stat().st_size == packed['bytes'] and sha(destination) == packed['sha256']
    decoded_sha = hashlib.sha256()
    decoded_bytes = 0
    with destination.open('rb') as source, zstandard.ZstdDecompressor().stream_reader(source) as decoded:
        for chunk in iter(lambda: decoded.read(1 << 20), b''):
            decoded_sha.update(chunk)
            decoded_bytes += len(chunk)
    assert decoded_sha.hexdigest() == proof['candidate']['sha256'] and decoded_bytes == proof['candidate']['bytes']
    evidence = directory / 'pack-evidence.zip'
    guest = """
import pathlib,sys,zipfile
root=pathlib.Path(ROOT)
names=['pack-result.json','acceptance-proof.json','bounded_stage.py']
names += [str(p.relative_to(root)) for p in sorted((root/'stages').rglob('*')) if p.is_file()]
with zipfile.ZipFile(sys.stdout.buffer,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for name in names:z.write(root/name,name)
""".replace('ROOT', repr(proof['guest_root']))
    with evidence.open('xb') as output:
        result = remote_capture.remote(guest, 60, output)
    assert result.returncode == 0, result.stderr.decode(errors='replace')
    with zipfile.ZipFile(evidence) as archive:
        assert archive.testzip() is None and json.loads(archive.read('pack-result.json')) == packed
        members = {name: {'bytes': len(archive.read(name)), 'sha256': hashlib.sha256(archive.read(name)).hexdigest()} for name in archive.namelist()}
    write(directory / 'pack-evidence-members.json', members)
    receipt = {'download_verified': True, 'path': str(destination), 'sha256': sha(destination), 'bytes': destination.stat().st_size,
        'decoded_sha256': decoded_sha.hexdigest(), 'decoded_bytes': decoded_bytes,
        'pack_evidence': str(evidence), 'pack_evidence_sha256': sha(evidence),
        'accepted_report_sha256': proof['accepted_report_sha256'], 'source_commit': proof['source_commit'],
        'runner_sha256': proof['runner_sha256'], 'native_evidence_sha256': proof['candidate']['native_evidence_sha256']}
    write(directory / 'packed-download-receipt.json', receipt)
    print(json.dumps(receipt), flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    p = sub.add_parser('prepare')
    p.add_argument('--case', choices=list(RECIPES['cases']), required=True)
    for name in ['replay-directory', 'report-sha256', 'execution-sha256', 'runner-sha256', 'source-commit', 'build-binding']:
        p.add_argument('--' + name, required=True)
    for action in ['pack', 'download']:
        sub.add_parser(action).add_argument('--directory', required=True)
    args = parser.parse_args()
    {'prepare': prepare, 'pack': pack, 'download': download}[args.action](args)
