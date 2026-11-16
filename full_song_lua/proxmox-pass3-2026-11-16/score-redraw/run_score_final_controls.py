import json, pathlib, shutil, sys

ROOT = pathlib.Path('/opt/song-lua-audit')
OUT = ROOT / 'pass3-score-final-controls'
assert not OUT.exists()
OUT.mkdir()
sys.path.insert(0, str(ROOT))
import worker_pass2 as w
w.RESULTS = OUT
harness = ROOT / 'bin/itgmania-harness-pass3-score-redraw'
native = ROOT / 'routine-native/ITGmania-harness-trace'
runner = ROOT / 'bin/full_song_lua-pass3-score-redraw-final'
oracle = json.loads((ROOT / 'pass3-score-harness-final/build-proof.json').read_text())
deadsync = json.loads((ROOT / 'pass3-score-redraw-build-final/build-proof.json').read_text())
assert w.sha(harness) == oracle['harness_binary_sha256']
assert w.sha(native) == oracle['native_binary_sha256']
assert w.sha(runner) == deadsync['runner_sha256']
w.write(OUT / 'source-proof.json', {'oracle': oracle, 'deadsync': deadsync})
for ident in ['score-queue-v2', 'score-redraw-manual', 'score-format']:
    dest = ROOT / 'Songs/__pass3_controls' / ident
    case = OUT / ident
    case.mkdir()
    trace = case / 'trace'
    trace.mkdir()
    result = {'id': ident, 'source_simfile': str((dest / 'control.sm').relative_to(ROOT / 'Songs')),
              'source_snapshot': {'oracle': oracle, 'deadsync': deadsync},
              'control_sha256': {p.name: w.sha(p) for p in dest.iterdir()},
              'status': 'running', 'started_at': w.now(), 'stages': {}}
    w.write(case / 'result.json', result)
    command = [harness, 'song-lua-trace', dest / 'control.sm', '--itgmania-bin', native,
               '--fallback-theme', 'Harness Simply Love', '--headless', '--game', 'dance', '--style', 'single',
               '--difficulty', 'Hard', '--chart-index', '1', '--until-gameplay-end', '--capture-fps', '60',
               '--max-events', '250000', '--timeout', '180', '--out', trace / 'native.json']
    if ident == 'score-redraw-manual':
        command += ['--player-options', 'default', '--autoplay', '0', '--input-script', dest / 'inputs.json']
    result['stages']['capture'] = w.execute(case, 'capture', command, 270, memory='3G')
    if result['stages']['capture']['exit'] != 0:
        log = (case / 'capture.log').read_text(errors='replace')
        result['status'] = w.failure_category('capture', result['stages']['capture'], log)
        result['reason'] = log[-8000:]
        artifact, facts = w.preserve_diagnostics(case)
        result['native_failure'] = facts
        if artifact:
            result['artifacts'] = [artifact]
    else:
        summary = w.document_summary(trace / 'native.json')
        assert summary['harness_version'] == '0.1.104'
        result['native'] = summary
        document = json.loads((trace / 'native.json').read_text())
        result['samples'] = [{'name': e['args'][0], 'values': e['args'][1]} for e in document['events']
                             if e.get('operation') == 'MessageManager.Broadcast' and e.get('args', [''])[0].startswith('Score')]
        result['native_artifact'] = w.compress(trace / 'native.json', remove=False)
        w.write(trace / '_semantic_manifest.json', {
            'fixture_schema_version': 1, 'oracle_schema_version': summary['schema_version'],
            'harness_version': summary['harness_version'],
            'itgmania': {'git_revision': summary['input']['native_source']['revision'], 'git_dirty': 'false'},
            'simfiles': [{'simfile': result['source_simfile'], 'fixture': 'native.json', 'title': ident,
                         'status': 'ok', 'command_observer': summary['command_observer']}],
        })
        result['stages']['archive'] = w.execute(case, 'archive', [harness, 'song-lua-archive', ROOT / 'Songs',
            '--traces', trace, '--out', case / 'candidate', '--uncompressed', '--theme-assets', ROOT / 'routine-theme'], 600, memory='6G')
        assert result['stages']['archive']['exit'] == 0
        entry = json.loads((case / 'candidate/index.json').read_text())['archives'][0]
        candidate = case / 'candidate' / entry['archive']
        result['candidate_sha256'] = w.sha(candidate)
        result['stages']['replay'] = w.execute(case, 'replay', [runner, '--archive', candidate, '--report', case / 'report.json'], 240, memory='6G')
        if (case / 'report.json').exists():
            c = w.document_summary(case / 'report.json', report=True)
            result['comparison'] = c
            result['status'] = 'pass' if result['stages']['replay']['exit'] == 0 and c['archive_accepted'] and c['mismatch_count'] == c['error_count'] == 0 else 'parity_failure'
            if result['status'] == 'pass':
                result['stages']['pack'] = w.execute(case, 'pack', [harness, 'song-lua-pack', candidate,
                    '--report', case / 'report.json', '--out', case / 'accepted'], 180, memory='6G')
                if result['stages']['pack']['exit']:
                    result['status'] = 'packaging_error'
                else:
                    packed = next((case / 'accepted').glob('*.tar.zst'))
                    result['accepted_artifact'] = {'file': str(packed.relative_to(OUT)), 'bytes': packed.stat().st_size,
                        'sha256': w.sha(packed), 'uncompressed_sha256': result['candidate_sha256']}
            result['report'] = w.compress(case / 'report.json', remove=False)
        else:
            result.update(status='replay_error', reason=(case / 'replay.log').read_text(errors='replace')[-8000:])
    result['finished_at'] = w.now()
    w.write(case / 'result.json', result)
    print(json.dumps({'id': ident, 'status': result['status'], 'comparison': result.get('comparison'), 'reason': result.get('reason')}), flush=True)
