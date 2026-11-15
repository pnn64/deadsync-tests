import collections,importlib.util,json,pathlib,sys
import ijson,zstandard
root=pathlib.Path('/opt/song-lua-audit')
sys.path.insert(0,str(root))
s=importlib.util.spec_from_file_location('analysis',root/'analyze-reports.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
groups=collections.defaultdict(list)
with (root/'results/8f4d4741245868cf/report.json.zst').open('rb') as f,zstandard.ZstdDecompressor().stream_reader(f) as z:
    for r in ijson.items(z,'mismatches.item',use_float=True):
        assert r['field']=='command_query_event'
        n=r['native'];groups[(n['scene'],n['seconds'],n['beat'])].append(r)
def equal(n,a):
    keys=['scene','kind','operation','source','line','seconds','beat']
    if n['kind'] in ['query','modifier']:keys+=['phase','args','results']
    elif n['kind']=='call':keys+=['phase','args','tween_time_left']
    elif n['kind']=='command':keys+=['command']
    return all(m.same(n.get(k),a.get(k)) for k in keys)
matched=0;unmatched=0;bad=[];permutations=0
for frame,records in groups.items():
    remaining=[r['deadsync'] for r in records];missing=[]
    for r in records:
        index=next((i for i,a in enumerate(remaining) if equal(r['native'],a)),None)
        if index is None:missing.append(r['native']);unmatched+=1
        else:remaining.pop(index);matched+=1
    if not missing:permutations+=1
    elif len(bad)<5:bad.append({'frame':frame,'unmatched_native':missing[:5],'unmatched_deadsync':remaining[:5]})
print(json.dumps({'total_mismatches':matched+unmatched,'frames_with_mismatches':len(groups),'pure_permutation_frames':permutations,'matched_after_reordering':matched,'unmatched_after_reordering':unmatched,'first_unmatched':bad,'comparison_semantics_version':3}))
