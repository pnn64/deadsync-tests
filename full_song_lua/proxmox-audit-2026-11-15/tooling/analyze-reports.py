"""Read all mismatches, not just the bounded preview, without loading a report."""
import collections,json,math,pathlib,sys
import ijson,zstandard
import worker
ROOT=worker.ROOT
def strict_json(a,b):
    if type(a)!=type(b):return False
    if isinstance(a,list):return len(a)==len(b) and all(strict_json(x,y) for x,y in zip(a,b))
    if isinstance(a,dict):return a.keys()==b.keys() and all(strict_json(a[k],b[k]) for k in a)
    return a==b
def same(a,b):
    if isinstance(a,bool) or isinstance(b,bool):return type(a)==type(b) and a==b
    if isinstance(a,(float,int)) and isinstance(b,(float,int)):return abs(a-b)<=1e-6
    if isinstance(a,list) and isinstance(b,list):return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    # Rust same_value recursively tolerates arrays, but falls back to exact
    # serde_json::Value equality for maps (including nested numeric types).
    if isinstance(a,dict) or isinstance(b,dict):return strict_json(a,b)
    return a==b
def summary(path):
    groups={};total=0
    with path.open('rb') as f,zstandard.ZstdDecompressor().stream_reader(f) as z:
        for mismatch in ijson.items(z,'mismatches.item',use_float=True):
            total+=1
            native=mismatch.get('native');actual=mismatch.get('deadsync')
            field=mismatch.get('field','unknown')
            if field=='command_query_event' and isinstance(native,dict) and isinstance(actual,dict):
                # Fresh harness 0.1.97 captures declare both native_constructor_queries
                # and native_modifier_results. Match same_call_event's exact keys.
                keys=['scene','kind','operation','source','line','seconds','beat']
                if native.get('kind') in ('query','modifier'):keys+=['phase','args','results']
                elif native.get('kind')=='call':keys+=['phase','args','tween_time_left']
                else:keys+=['command']
                differences=[k for k in keys if not same(native.get(k),actual.get(k))]
                identity=(field,native.get('operation'),actual.get('operation'),tuple(differences))
                compact={'native':{k:worker.bounded(native[k]) for k in keys if k in native},
                         'deadsync':{k:worker.bounded(actual[k]) for k in keys if k in actual}}
                if 'tween_time_left' in differences:compact['native_tween_children']=worker.bounded(native.get('detail',{}).get('native_tween_children'))
                location={'source':native.get('source'),'line':native.get('line')}
            else:
                identity=(field,None,None,());differences=[];compact=worker.bounded(mismatch);location=None
            if identity not in groups:
                assert len(groups)<2000,'unexpected mismatch-group count; keep full report for inspection'
                groups[identity]={'field':field,'native_operation':identity[1],'deadsync_operation':identity[2],
                                  'different_fields':differences,'count':0,'first_example':compact,'locations':[]}
            group=groups[identity];group['count']+=1
            if location and location not in group['locations'] and len(group['locations'])<12:group['locations'].append(location)
    return {'analysis_version':3,'comparison_profile':'native_constructor_queries=true; native_modifier_results=true',
            'total_mismatches':total,'groups':sorted(groups.values(),key=lambda g:-g['count'])}
def main():
    count=0
    for case in (ROOT/'results').iterdir():
        if not case.is_dir() or case.name.startswith('pilot-') or not (case/'result.json').exists():continue
        result=json.loads((case/'result.json').read_text())
        if not result.get('finished_at'):continue
        source=result;label='primary'
        if (case/'video-recheck.json').exists():source=json.loads((case/'video-recheck.json').read_text());label='video-recheck'
        if not source.get('comparison') or not source['comparison'].get('mismatch_count'):continue
        artifact=next((a for a in source.get('artifacts',[]) if a['file'].endswith('report.json.zst')),None)
        if not artifact:continue
        target=case/('mismatch-analysis-'+label+'.json')
        if target.exists() and json.loads(target.read_text()).get('analysis_version')==3:continue
        data=summary(ROOT/'results'/artifact['file']);data['report_sha256']=artifact['sha256'];data['report_file']=artifact['file']
        assert data['total_mismatches']==source['comparison']['mismatch_count']
        worker.write(target,data);count+=1
    print(json.dumps({'reports_analyzed':count}))
if __name__=='__main__':main()
