import collections,json,pathlib,sys
import ijson,zstandard
root=pathlib.Path('/opt/song-lua-audit');case=root/'results'/sys.argv[1]
r=json.loads((case/'result.json').read_text());source=r
if (case/'video-recheck.json').exists():source=json.loads((case/'video-recheck.json').read_text())
a=next(a for a in source['artifacts'] if a['file'].endswith('report.json.zst'))
frames={};counts=collections.Counter()
with (root/'results'/a['file']).open('rb') as f,zstandard.ZstdDecompressor().stream_reader(f) as z:
 for m in ijson.items(z,'mismatches.item',use_float=True):
  if m.get('field')!='command_query_event':continue
  n=m.get('native',{});d=m.get('deadsync',{})
  if n.get('tween_time_left')==d.get('tween_time_left'):continue
  k=n['seconds'];counts[(n['tween_time_left'],d['tween_time_left'])]+=1
  frames.setdefault(k,{'seconds':k,'beat':n['beat'],'native':n['tween_time_left'],'deadsync':d['tween_time_left'],'operations':[]})['operations'].append(n['operation'])
print(json.dumps({'id':r['id'],'source_simfile':r['source_simfile'],'frame_count':len(frames),'frames':list(frames.values()),'value_pair_count':len(counts)},ensure_ascii=False))
