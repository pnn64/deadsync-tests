"""Copy verified accepted artifacts, keeping only split parts for large files."""
import hashlib,json,pathlib,subprocess,tarfile,shutil,os
import zstandard
from remote import ssh,WORK
store=pathlib.Path('C:/GitHub/deadsync/tests/fixtures/full_song_lua')
receipt_path=WORK/'published-archives.json'
receipts=json.loads(receipt_path.read_text()) if receipt_path.exists() else []
known={x['sha256'] for x in receipts}
rows=json.loads((WORK/'all-results.json').read_text())+json.loads((WORK/'extra-results.json').read_text())
if (WORK/'final-results.json').exists():rows+=json.loads((WORK/'final-results.json').read_text())
latest={r['id']:r for r in rows}
split=json.loads((store/'split-archives.json').read_text())
entries={e['archive']:e for e in split['archives']}
catalog={r['archive']:r for r in json.loads((store/'committed-songs.json').read_text())}
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for r in latest.values():
 if r['status']!='pass':continue
 a=next(a for a in r['artifacts'] if '/accepted/' in a['file'])
 if a['sha256'] in known:continue
 if os.environ.get('PUBLISH_IP') and r['ip']!=os.environ['PUBLISH_IP']:continue
 assert shutil.disk_usage(store).free>a['bytes']*2+1500000000,'space reserve'
 directory=r.get('result_directory','pass2-results')
 remote='/opt/song-lua-audit/'+directory+'/'+a['file']
 pending=WORK/('publish-'+a['sha256']+'.tmp')
 with pending.open('wb') as f:
  child=subprocess.Popen(ssh(r['ip'])+['cat',remote],stdout=f)
  assert child.wait()==0,remote
 assert pending.stat().st_size==a['bytes'] and sha(pending)==a['sha256']
 digest=hashlib.sha256()
 with pending.open('rb') as f,zstandard.ZstdDecompressor().stream_reader(f) as decoded:
  while block:=decoded.read(4*1024*1024):digest.update(block)
 assert digest.hexdigest()==a['uncompressed_sha256']
 with pending.open('rb') as f,zstandard.ZstdDecompressor().stream_reader(f) as decoded,tarfile.open(fileobj=decoded,mode='r|') as tar:
  member=next(iter(tar));assert member.name=='manifest.json';manifest=json.load(tar.extractfile(member))
 name=pathlib.PurePosixPath(a['file']).name
 assert name==a['sha256']+'.tar.zst'
 if a['bytes']>=50000000:
  parts_dir=store/'archive-parts'/a['sha256'];parts_dir.mkdir(parents=True,exist_ok=True);parts=[]
  with pending.open('rb') as f:
   while block:=f.read(48000000):
    part=parts_dir/(f'{len(parts):03}.part');part.write_bytes(block)
    parts.append(dict(file=part.relative_to(store).as_posix(),bytes=len(block),sha256=sha(part)))
  assert sum(p['bytes'] for p in parts)==a['bytes']
  entries[name]=dict(archive=name,bytes=a['bytes'],sha256=a['sha256'],parts=parts)
 else:
  dest=store/name
  assert not dest.exists() or sha(dest)==a['sha256']
  shutil.copyfile(pending,dest)
 catalog[name]=dict(title=manifest['chart']['title'],source_simfile=manifest['chart']['source_path'],harness_version=manifest['harness_version'],archive=name)
 receipts.append(dict(id=r['id'],ip=r['ip'],remote=remote,**a,archive=name,decoded_sha256_verified=True,source_snapshot=r['source_snapshot']))
 receipt_path.write_text(json.dumps(receipts,indent=2)+'\n')
 (store/'split-archives.json').write_text(json.dumps({'version':1,'archives':sorted(entries.values(),key=lambda e:e['archive'])},indent=2)+'\n')
 ignore=store.parent/'.gitignore';marker='# Restored split archives (managed by prepare_test_fixtures.py)'
 before=ignore.read_text().split(marker)[0].rstrip()
 ignore.write_text(before+'\n\n'+marker+'\n/full_song_lua/.fixture-*\n'+'\n'.join('/full_song_lua/'+n for n in sorted(entries))+'\n')
 (store/'committed-songs.json').write_text(json.dumps([catalog[n] for n in sorted(catalog)],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (store/'committed-archives.txt').write_text('\n'.join(sorted(catalog))+'\n')
 pending.unlink();known.add(a['sha256']);print(r['source_simfile']+' '+name,flush=True)
print('Published verified archives: '+str(len(receipts)),flush=True)
