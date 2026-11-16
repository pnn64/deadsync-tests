import hashlib, json, pathlib, shutil, subprocess
from remote import WORK, run, ssh
IP = '192.168.1.23'
DEST = WORK / 'score-redraw-collected'
script = '''import hashlib,json,pathlib
root=pathlib.Path('/opt/song-lua-audit');paths=[]
folders=['pass3-native-score-queue-baseline','pass3-native-score-queue-v2-baseline',
 'pass3-native-score-redraw-candidate','pass3-native-score-redraw-manual',
 'pass3-native-score-redraw-theme-v2','pass3-native-score-format',
 'pass3-score-redraw-baseline-results','pass3-score-redraw-build',
 'pass3-score-redraw-build-resume','pass3-score-redraw-build-feature',
 'pass3-score-redraw-build-format','pass3-score-redraw-compat-audit',
 'pass3-score-redraw-build-final','pass3-score-harness-final',
 'pass3-score-final-controls','pass3-score-regressions']
names=['result.json','source-proof.json','build-proof.json','native.json.zst','report.json.zst',
 'native-diagnostics.tar.zst','capture.log','capture-service.log','archive.log','archive-service.log',
 'replay.log','replay-service.log','score-tests.log','native-gameplay-tests.log',
 'compat-tests.log','before-score-fix.log','candidate-compat.log','audit.json',
 'validation.json','unit-tests.log','harness-build.log','pack.log','pack-service.log']
for folder in folders:
 base=root/folder
 if not base.exists():continue
 for directory in [base]+[p for p in base.iterdir() if p.is_dir() and p.name!='baseline-theme']:
  result=directory/'result.json'
  if result.exists():assert json.loads(result.read_text())['status']!='running'
  paths.extend(directory/name for name in names if (directory/name).is_file())
  if (directory/'trace/native.json.zst').exists():paths.append(directory/'trace/native.json.zst')
for name in ['score-queue','score-queue-v2','score-redraw','score-redraw-manual','score-format']:
 paths.extend(p for p in (root/'Songs/__pass3_controls'/name).iterdir() if p.is_file())
paths.extend((root/'pass3-native-score-redraw-candidate/baseline-theme').rglob('*.lua'))
for name in ['audit_score_compat.py','build_score_redraw_final.py','build_score_harness_final.py',
             'run_score_final_controls.py','run_score_regressions.py',
             'run_score_validation_sequence.py','run_score_validation_sequence_v2.py',
             'pass3-score-validation-sequence.json','pass3-score-validation-sequence-v2.json']:
 paths.append(root/name)
for suffix in ['score-redraw-build','score-redraw-build-resume','score-redraw-build-feature',
               'score-redraw-build-format','score-compat-audit','score-redraw-build-final',
               'score-harness-final','score-validation-sequence','score-validation-sequence-v2']:
 p=root/'logs'/('pass3-'+suffix+'.log')
 if p.exists():paths.append(p)
rows=[]
for p in paths:
 with p.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
 rows.append({'source':str(p),'local':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':digest})
print(json.dumps(rows))
'''
rows = json.loads(run(script, ip=IP, capture_output=True).stdout)
assert shutil.disk_usage(WORK).free > sum(r['bytes'] for r in rows) * 2 + 256 * 1024 * 1024
print(json.dumps({'files': len(rows), 'bytes': sum(r['bytes'] for r in rows)}), flush=True)
for row in rows:
    path = DEST / row['local']
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        subprocess.run(['scp', *ssh(IP)[1:-1], 'parity@' + IP + ':' + row['source'], str(path)], check=True)
    assert path.stat().st_size == row['bytes']
    with path.open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest() == row['sha256'], row['local']
(DEST / 'manifest.json').write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')
print('All score-control evidence copied and SHA-256 verified.', flush=True)
