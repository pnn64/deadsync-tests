import json, os, pathlib, sys

ROOT = pathlib.Path('/opt/song-lua-audit')
OUT = ROOT / 'pass3-score-regressions'
assert not OUT.exists()
OUT.mkdir()
sys.path.insert(0, str(ROOT))
import worker_pass2 as w
w.RESULTS = OUT
proof = json.loads((ROOT / 'pass3-score-redraw-build-final/build-proof.json').read_text())
runner = ROOT / 'bin/full_song_lua-pass3-score-redraw-final'
assert w.sha(runner) == proof['runner_sha256']
w.write(OUT / 'source-proof.json', proof)
origins = [ROOT / 'pass3-routine-stats-observed-results' / name for name in [
    'routine-life-dance', 'routine-life-pump', 'style-dance-routine', 'style-pump-routine',
    'routine-manual-dance', 'routine-manual-pump', 'routine-fail-dance', 'routine-fail-pump',
]] + [ROOT / 'pass3-routine-stats-shark-results' / name for name in ['68eda87bf02562c3', '730650ffb42269d8']]
for origin in origins:
    old = json.loads((origin / 'result.json').read_text())
    assert old['status'] == 'pass'
    source = origin / (old['candidate_sha256'] + '.tar')
    assert w.sha(source) == old['candidate_sha256']
    case = OUT / old['id']
    case.mkdir()
    candidate = case / source.name
    os.link(source, candidate)
    result = {'id': old['id'], 'source_simfile': old['source_simfile'], 'profile': old.get('profile'),
              'source_snapshot': {'deadsync': proof, 'native': old['source_snapshot']}, 'native': old['native'],
              'capture_reused': True, 'candidate_reused': str(source), 'baseline_result': str(origin / 'result.json'),
              'candidate_sha256': old['candidate_sha256'], 'status': 'running', 'started_at': w.now(), 'stages': {}}
    w.write(case / 'result.json', result)
    result['stages']['replay'] = w.execute(case, 'replay', [runner, '--archive', candidate, '--report', case / 'report.json'], 600, memory='6G')
    if (case / 'report.json').exists():
        c = w.document_summary(case / 'report.json', report=True)
        result['comparison'] = c
        assert c['fixture_sha256'] == old['candidate_sha256']
        result['status'] = 'pass' if result['stages']['replay']['exit'] == 0 and c['archive_accepted'] and c['mismatch_count'] == c['error_count'] == 0 else 'parity_failure'
        result['report'] = w.compress(case / 'report.json', remove=False)
    else:
        result.update(status='replay_error', reason=(case / 'replay.log').read_text(errors='replace')[-8000:])
    result['finished_at'] = w.now()
    w.write(case / 'result.json', result)
    print(json.dumps({'id': result['id'], 'status': result['status'], 'mismatches': result.get('comparison', {}).get('mismatch_count'),
                      'fields': result.get('comparison', {}).get('mismatch_fields'), 'errors': result.get('comparison', {}).get('errors')}), flush=True)
