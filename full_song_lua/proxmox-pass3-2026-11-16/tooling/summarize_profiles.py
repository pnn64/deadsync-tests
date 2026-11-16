"""Resolve samply's portable symbol sidecars and summarize sampled CPU stacks."""
import collections,gzip,json,pathlib,subprocess,sys,time
ROOT=pathlib.Path('/opt/song-lua-audit/pass3-profiles')
def summarize(directory):
    with gzip.open(directory/'profile.json.gz','rt') as f:profile=json.load(f)
    symbols=json.loads((directory/'profile.json.syms.json').read_text())
    libraries={row['debug_name']:row for row in symbols['data']}
    addresses={name:dict(row['known_addresses']) for name,row in libraries.items()}
    exclusive=collections.Counter();inclusive=collections.Counter();total=0;unknown=0
    for thread in profile['threads']:
        frames=thread['frameTable'];functions=thread['funcTable'];resources=thread['resourceTable']
        names=[]
        for index,func in enumerate(frames['func']):
            resource=functions['resource'][func]
            lib_index=resources['lib'][resource] if resource is not None and resource>=0 else None
            lib=profile['libs'][lib_index] if lib_index is not None else {}
            name=lib.get('debugName');address=frames['address'][index]
            symbol_index=addresses.get(name,{}).get(address)
            if symbol_index is not None:
                entry=libraries[name]['symbol_table'][symbol_index]
                names.append(symbols['string_table'][entry['symbol']])
            else:
                names.append('[unresolved] '+str(name or thread['stringArray'][functions['name'][func]]))
        samples=thread['samples'];weights=samples.get('weight') or [1]*samples['length']
        leaves=collections.Counter()
        for leaf,weight in zip(samples['stack'],weights):
            if leaf is not None:leaves[leaf]+=weight
        stacks=thread['stackTable']
        for leaf,weight in leaves.items():
            total+=weight;name=names[stacks['frame'][leaf]];exclusive[name]+=weight
            if name.startswith('[unresolved]'):unknown+=weight
            seen=set();cursor=leaf
            while cursor is not None:
                seen.add(names[stacks['frame'][cursor]]);cursor=stacks['prefix'][cursor]
            for name in seen:inclusive[name]+=weight
    def top(counter):return [{'function':name,'samples':count,'percent':round(100*count/total,3)} for name,count in counter.most_common(30)]
    result={'sampled_stacks':total,'unresolved_leaf_samples':unknown,'exclusive':top(exclusive),'inclusive':top(inclusive),
            'method':'Weighted CPU stack samples; physical symbols resolved from exact samply known_addresses. Recursive inclusive frames counted once per sample. No inline expansion.'}
    (directory/'hotspots.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

def refresh():
    rows=[]
    for p in sorted(ROOT.glob('*/run-*/result.json')):
        run=json.loads(p.read_text())
        if run.get('status')!='complete':continue
        hotspots=summarize(p.parent)
        rows.append((p.parent.relative_to(ROOT),run,hotspots))
    if not rows:return
    lines=['# Heavy song Lua CPU profiles','',
        'Baseline collection on Proxmox: two vCPUs, 64 GiB guest RAM, 58 GiB process limit, samply 0.13.1 at 99 Hz. '
        'Each profile covers a complete replay with archive validation and report generation. Archive decompression happened before recording. '
        'OS caches were not cleared; these are repeated runs, not controlled cold/warm benchmarks.','',
        'The release runner retains debug information and frame pointers, with LTO disabled and 16 codegen units. '
        'See [build provenance](build-proof.json) for the exact baseline source, preserved worktree edits and executable hash. '
        'These are baseline profiles collected concurrently with correctness work, not profiles of subsequent fixes.','',
        '| Fixture | Run | Replay + profiler seconds | CPU samples | Replay passed | Unresolved leaf samples |',
        '| --- | --- | ---: | ---: | --- | ---: |']
    for rel,run,hot in rows:
        lines.append(f"| {run['song']} | {run['iteration']} | {run['execution']['elapsed_seconds']} | {hot['sampled_stacks']} | {run['parity_pass']} | {hot['unresolved_leaf_samples']} |")
    lines+=['','Percentages below are shares of sampled CPU stacks, not wall-clock shares. Exclusive samples identify the currently executing physical function; inclusive samples include descendants and overlap. '
        'Full inclusive/exclusive top-30 tables are in each hotspots.json. Portable .syms.json files accompany every saved profile.','']
    for rel,run,hot in rows:
        lines += [f"## {run['song']} — run {run['iteration']}",'',
            f'[Profile]({rel.as_posix()}/profile.json.gz) · [Symbols]({rel.as_posix()}/profile.json.syms.json) · [Hotspot data]({rel.as_posix()}/hotspots.json) · [Run provenance]({rel.as_posix()}/result.json)','',
            '| Exclusive CPU samples | Function |','| ---: | --- |']
        for entry in hot['exclusive'][:12]:
            name=entry['function'].replace('|','&#124;')
            lines.append(f"| {entry['percent']:.2f}% | `{name}` |")
        lines.append('')
    (ROOT/'README.md').write_text('\n'.join(lines)+'\n')
    print('Summarized completed profiles:',len(rows),flush=True)

refresh()
if '--watch' in sys.argv:
    while True:
        state=subprocess.check_output(['systemctl','show','song-lua-pass3-profiles','-p','ActiveState','--value'],text=True).strip()
        if state not in ['active','activating']:break
        time.sleep(30)
        refresh()
    refresh()
