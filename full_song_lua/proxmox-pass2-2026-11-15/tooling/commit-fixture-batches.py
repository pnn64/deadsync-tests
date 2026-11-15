"""Publish complete archive/catalog batches below the remote pack-size limit."""
import hashlib,json,pathlib,subprocess,shutil
from remote import WORK
repo=pathlib.Path('C:/GitHub/deadsync/tests/fixtures');store=repo/'full_song_lua'
git=['git','-C',str(repo),'-c','gc.auto=0','-c','pack.threads=2','-c','pack.windowMemory=128m']
def get(*args):return subprocess.check_output(git+list(args))
def call(*args):subprocess.run(git+list(args),check=True)
def staged_text(path,text):
 oid=subprocess.check_output(git+['hash-object','-w','--stdin'],input=text.encode()).decode().strip()
 call('update-index','--add','--cacheinfo','100644,'+oid+','+path)
assert not get('diff','--cached','--name-only').strip()
receipts=json.loads((WORK/'published-archives.json').read_text())
final=json.loads((WORK/'final-results.json').read_text())
verified={a['sha256'] for r in final if r['status']=='pass' for a in r['artifacts'] if '/accepted/' in a['file']}
catalog={r['archive']:r for r in json.loads(get('show','HEAD:full_song_lua/committed-songs.json'))}
available={r['archive']:r for r in json.loads((store/'committed-songs.json').read_text(encoding='utf-8'))}
split={r['archive']:r for r in json.loads(get('show','HEAD:full_song_lua/split-archives.json'))['archives']}
all_split={r['archive']:r for r in json.loads((store/'split-archives.json').read_text())['archives']}
remaining=[r for r in receipts if r['archive'] not in catalog and r['sha256'] in verified]
print('Ready to publish',len(remaining),'verified final archives',flush=True)
log=[]
call('push','--quiet','origin','HEAD:main')
while remaining:
 group=[];size=0
 while remaining and (not group or size+remaining[0]['bytes']<900000000):
  row=remaining.pop(0);group.append(row);size+=row['bytes']
 assert shutil.disk_usage(repo).free>size+800000000,'insufficient disk reserve for Git objects'
 for r in group:
  name=r['archive'];catalog[name]=available[name]
  if name in all_split:
   entry=all_split[name];split[name]=entry
   for part in entry['parts']:
    p=store/part['file'];assert p.stat().st_size==part['bytes']
    with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==part['sha256']
   paths=['full_song_lua/'+p['file'] for p in entry['parts']]
  else:
   p=store/name
   with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['sha256']
   paths=['full_song_lua/'+name]
  call('add','--',*paths)
 staged_text('full_song_lua/committed-songs.json',json.dumps([catalog[n] for n in sorted(catalog)],ensure_ascii=False,indent=2)+'\n')
 staged_text('full_song_lua/committed-archives.txt','\n'.join(sorted(catalog))+'\n')
 staged_text('full_song_lua/split-archives.json',json.dumps({'version':1,'archives':[split[n] for n in sorted(split)]},indent=2)+'\n')
 marker='# Restored split archives (managed by prepare_test_fixtures.py)'
 prefix=(repo/'.gitignore').read_text().split(marker)[0].rstrip()
 staged_text('.gitignore',prefix+'\n\n'+marker+'\n/full_song_lua/.fixture-*\n'+'\n'.join('/full_song_lua/'+n for n in sorted(split))+'\n')
 body=WORK/'fixture-commit-message.txt'
 body.write_text('test(song-lua): add refreshed native parity fixtures\n\n'+f'Add {len(group)} hash-verified archives accepted by the final patched replay.\nKeep split archive parts and catalogs complete in this commit.\n\n'+ '\n'.join('- '+r['id']+': '+available[r['archive']]['source_simfile'] for r in group)+'\n',encoding='utf-8')
 call('commit','--quiet','-F',str(body))
 head=get('rev-parse','HEAD').decode().strip()
 call('push','--quiet','origin','HEAD:main')
 remote=get('ls-remote','origin','refs/heads/main').decode().split()[0];assert remote==head
 record={'commit':head,'bytes':size,'archives':[r['archive'] for r in group],'remote_verified':True}
 receipt=WORK/'fixture-pushes.json';history=json.loads(receipt.read_text()) if receipt.exists() else []
 history.append(record);receipt.write_text(json.dumps(history,indent=2)+'\n')
 print('Pushed',head[:10],len(group),'archives',round(size/2**20),'MiB',flush=True)
