import collections,datetime,hashlib,json,pathlib
paths=list(pathlib.Path('/opt/song-lua-audit/results/82dbf1390bb50291-large/tmp').glob('itgmania-harness-rs/song-lua-*/Save/itgmania-harness/*.events.new'))
assert len(paths)==1
p=paths[0];size=p.stat().st_size
with p.open('rb') as f:
 start=max(0,size-16*1024*1024);f.seek(start);raw=f.read(size-start)
text=raw.decode(errors='replace');decoder=json.JSONDecoder();index=0;events=[]
while index<len(text):
 index=text.find('{',index)
 if index<0:break
 try:value,end=decoder.raw_decode(text,index)
 except json.JSONDecodeError:index+=1;continue
 index=end
 if isinstance(value,dict) and all(k in value for k in ['seq','operation','kind','scene']):events.append(value)
assert len(events)>100 and all(b['seq']>a['seq'] for a,b in zip(events,events[1:]))
result={'sampled_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'case_id':'82dbf1390bb50291-large','method':'Bounded 16 MiB tail sample of the live native event stream; not an all-events histogram','stream_bytes':size,'start_byte':start,'sample_sha256':hashlib.sha256(raw).hexdigest(),'complete_events':len(events),'first':events[0],'last':events[-1],
 'operations':dict(collections.Counter(e['operation'] for e in events).most_common()),'contexts':[{'source':k[0],'command':k[1],'count':v} for k,v in collections.Counter((e.get('source'),e.get('command')) for e in events).most_common()]}
print(json.dumps(result))
