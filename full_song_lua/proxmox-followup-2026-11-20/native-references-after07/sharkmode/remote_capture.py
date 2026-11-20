"""Upload, run once, and download an isolated Shark capture on owned guest1503."""
import base64
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parent
GUEST_ROOT = '/opt/song-lua-audit/parity-20261120/sharkmode-current-b2-attempt01'

def digest(path):
    with Path(path).open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def write(path, value):
    with path.open('x', encoding='utf-8') as output:
        json.dump(value, output, indent=2)
        output.write('\n')

def host_code(guest, timeout):
    return """
import json,pathlib,subprocess,sys
row=next(r for r in json.loads(pathlib.Path('/root/deadsync-lua-20261119/fleet.json').read_bytes()) if r['vmid']==1503)
assert row['ip']=='192.168.1.37', row['ip']
cmd=['ssh','-i','/root/deadsync-pass3-20261116/transfer-key','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
 '-o','UserKnownHostsFile=/root/deadsync-lua-20261119/fleet-known-hosts','-o','ConnectTimeout=10','parity@'+row['ip'],'python3','-']
r=subprocess.run(cmd,input=GUEST.encode(),timeout=TIMEOUT)
raise SystemExit(r.returncode)
""".replace('GUEST', repr(guest)).replace('TIMEOUT', str(timeout))

def remote(guest, timeout=60, output=None):
    code = host_code(guest, timeout)
    return subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10',
        'root@192.168.1.79', 'python3', '-'], input=code.encode(),
        stdout=output if output is not None else subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout + 30)

def upload():
    package = ROOT / 'input-package.zip'
    receipt = json.loads((ROOT / 'input-package.json').read_bytes())
    assert digest(package) == receipt['sha256'] and package.stat().st_size == receipt['bytes']
    guest = """
import base64,hashlib,io,json,pathlib,shutil,subprocess,zipfile
root=pathlib.Path(ROOT)
assert not root.exists(), 'exclusive attempt directory already exists'
disk=dict(zip(['total','used','free'],shutil.disk_usage(root.parent)))
assert disk['free']>=8*1024**3
ps=subprocess.run(['ps','-eo','pid,ppid,comm,args'],capture_output=True,text=True,check=True).stdout
active=[line for line in ps.splitlines() if any(s in line for s in ['ITGmania-harness-trace','itgmania-harness-rs','full_song_lua-','/cargo ','/rustc '])]
assert not active,active
raw=base64.b64decode(PAYLOAD)
assert hashlib.sha256(raw).hexdigest()==EXPECTED
with zipfile.ZipFile(io.BytesIO(raw)) as z:
 assert z.testzip() is None
 names=z.namelist();assert len(names)==len(set(names))
 assert all(not pathlib.PurePosixPath(n).is_absolute() and '..' not in pathlib.PurePosixPath(n).parts and '\\\\' not in n for n in names)
 root.mkdir()
 for name in names:
  path=root/name;path.parent.mkdir(parents=True,exist_ok=True)
  with path.open('xb') as out:out.write(z.read(name))
proof={'vmid':1503,'root':str(root),'input_package_sha256':EXPECTED,'input_package_bytes':len(raw),'disk_before':disk,'active_competing_jobs':active}
with (root/'upload-receipt.json').open('x') as out:json.dump(proof,out,indent=2)
print(json.dumps(proof),flush=True)
""".replace('ROOT', repr(GUEST_ROOT)).replace('PAYLOAD', repr(base64.b64encode(package.read_bytes()).decode())).replace('EXPECTED', repr(receipt['sha256']))
    result = remote(guest, 90)
    value = {'started_action': 'upload', 'finished_at': now(), 'exit': result.returncode,
        'stdout': result.stdout.decode(errors='replace'), 'stderr': result.stderr.decode(errors='replace')}
    write(ROOT / 'upload-execution.json', value)
    print(json.dumps(value), flush=True)
    raise SystemExit(result.returncode)

def capture():
    assert not (ROOT / 'capture-execution.json').exists(), 'do not replay a completed invocation'
    upload_result = json.loads((ROOT / 'upload-execution.json').read_bytes())
    assert upload_result['exit'] == 0
    guest = """
import pathlib,subprocess,sys
root=pathlib.Path(ROOT)
assert not (root/'run-started.json').exists(), 'one attempt only'
raise SystemExit(subprocess.run(['python3',str(root/'run_native.py')],cwd=root).returncode)
""".replace('ROOT', repr(GUEST_ROOT))
    started = now()
    result = remote(guest, 2400)
    value = {'action': 'capture-and-archive', 'started_at': started, 'finished_at': now(),
        'vmid': 1503, 'guest_root': GUEST_ROOT, 'exit': result.returncode,
        'stdout': result.stdout.decode(errors='replace'), 'stderr': result.stderr.decode(errors='replace'),
        'run_native_sha256': digest(ROOT / 'run_native.py'), 'bounded_stage_sha256': digest(ROOT / 'bounded_stage.py'),
        'input_package_sha256': digest(ROOT / 'input-package.zip')}
    write(ROOT / 'capture-execution.json', value)
    print(json.dumps(value), flush=True)
    raise SystemExit(result.returncode)

def download():
    execution = json.loads((ROOT / 'capture-execution.json').read_bytes())
    assert execution['exit'] == 0
    result = remote("import pathlib,sys\np=pathlib.Path(" + repr(GUEST_ROOT + '/capture-result.json') + ")\nsys.stdout.buffer.write(p.read_bytes())\n")
    assert result.returncode == 0, result.stderr.decode(errors='replace')
    capture = json.loads(result.stdout)
    assert capture['capture_validated'] is True and capture['parity_accepted'] is False
    candidate = capture['candidate']
    assert candidate['path'] == GUEST_ROOT + '/candidate/' + candidate['sha256'] + '.tar'
    destination = ROOT / 'download' / (candidate['sha256'] + '.tar')
    destination.parent.mkdir(exist_ok=False)
    guest = "import pathlib,shutil,sys\np=pathlib.Path(" + repr(candidate['path']) + ")\nwith p.open('rb') as source:shutil.copyfileobj(source,sys.stdout.buffer,1<<20)\n"
    with destination.open('xb') as output:
        result = remote(guest, 180, output)
    assert result.returncode == 0, result.stderr.decode(errors='replace')
    assert destination.stat().st_size == candidate['bytes'] and digest(destination) == candidate['sha256']
    proof_path = ROOT / 'native-capture-evidence.zip'
    guest = """
import pathlib,sys,zipfile
root=pathlib.Path(ROOT)
names=['capture-result.json','native-summary.json','run-started.json','upload-receipt.json','run_native.py','bounded_stage.py',
 'source-and-recipe.json','bounded-stage-source.json','retained-accepted-references.json','traces/_semantic_manifest.json','candidate/index.json']
names += [str(p.relative_to(root)) for folder in ['provenance','stages'] for p in sorted((root/folder).rglob('*')) if p.is_file()]
with zipfile.ZipFile(sys.stdout.buffer,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for name in names:z.write(root/name,name)
""".replace('ROOT', repr(GUEST_ROOT))
    with proof_path.open('xb') as output:
        result = remote(guest, 60, output)
    assert result.returncode == 0, result.stderr.decode(errors='replace')
    with zipfile.ZipFile(proof_path) as archive:
        assert archive.testzip() is None
        assert json.loads(archive.read('capture-result.json')) == capture
        for name in ['run_native.py', 'bounded_stage.py', 'source-and-recipe.json']:
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest(ROOT / name)
        member_hashes = {n: {'bytes': len(archive.read(n)), 'sha256': hashlib.sha256(archive.read(n)).hexdigest()} for n in archive.namelist()}
    write(ROOT / 'native-capture-evidence-members.json', member_hashes)
    value = {'download_verified': True, 'candidate': {'path': str(destination), 'sha256': digest(destination), 'bytes': destination.stat().st_size},
        'native_capture_evidence': {'path': str(proof_path), 'sha256': digest(proof_path), 'bytes': proof_path.stat().st_size},
        'capture': capture, 'current_main_replay_required': True}
    write(ROOT / 'download-receipt.json', value)
    print(json.dumps(value), flush=True)

if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ['upload', 'capture', 'download']
    {'upload': upload, 'capture': capture, 'download': download}[sys.argv[1]]()
