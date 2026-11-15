"""Check catalogs and streamed archive parts without restoring large archives."""
import hashlib,json,pathlib,subprocess,datetime
from remote import WORK
repo=pathlib.Path('C:/GitHub/deadsync/tests/fixtures');store=repo/'full_song_lua'
rows=json.loads((store/'committed-songs.json').read_text(encoding='utf-8'))
names=[r['archive'] for r in rows]
assert names==sorted(set(names))
assert names==(store/'committed-archives.txt').read_text().splitlines()
entries=json.loads((store/'split-archives.json').read_text())['archives']
split={e['archive']:e for e in entries};assert len(split)==len(entries)
tracked=set(subprocess.check_output(['git','-C',str(repo),'ls-files','-z']).decode().split('\0'))
byte_count=0;parts_count=0
for name in names:
 expected=name.removesuffix('.tar.zst');assert len(expected)==64
 digest=hashlib.sha256()
 if name in split:
  e=split[name];assert e['sha256']==expected;size=0
  for part in e['parts']:
   p=store/part['file'];assert 'full_song_lua/'+part['file'] in tracked,part['file']
   assert p.stat().st_size==part['bytes'];size+=p.stat().st_size
   one=hashlib.sha256()
   with p.open('rb') as f:
    while block:=f.read(4*1024*1024):one.update(block);digest.update(block)
   assert one.hexdigest()==part['sha256'],part['file'];parts_count+=1
  assert size==e['bytes'];byte_count+=size
 else:
  p=store/name;assert 'full_song_lua/'+name in tracked,name
  with p.open('rb') as f:
   while block:=f.read(4*1024*1024):digest.update(block)
  byte_count+=p.stat().st_size
 assert digest.hexdigest()==expected,name
published=json.loads((WORK/'published-archives.json').read_text());assert all(r['archive'] in names and r['decoded_sha256_verified'] for r in published)
proof={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'archive_count':len(names),'split_parts_verified':parts_count,'compressed_bytes_verified':byte_count,'new_archives_with_decoded_hash_verified':len(published),'all_catalog_inputs_tracked':True,'restored_split_archives':False}
(WORK/'fixture-catalog-validation.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof))
