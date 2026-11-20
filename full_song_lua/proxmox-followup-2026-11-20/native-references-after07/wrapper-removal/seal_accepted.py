"""Seal compact exact capture/replay/pack evidence for parent fixture integration."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent

def sha(path):
    with Path(path).open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()

def write(path, value):
    with path.open('x', encoding='utf-8') as output:
        json.dump(value, output, indent=2)
        output.write('\n')

def summarize(report):
    fields = ['execution_path', 'archive_accepted', 'native_frames', 'replayed_frames', 'checked_stage_samples',
        'compared_stage_fields', 'diagnostic_compared_stage_fields', 'production_preparation_exercised',
        'diagnostic_replay_checks_passed', 'production_gameplay_checks_passed', 'capture_completed_gameplay',
        'whole_song_parity_proven', 'production_parity_proven', 'pixel_parity_proven']
    interactive_fields = ['draw_samples_compared', 'submitted_vertices_compared', 'draw_mismatches',
        'typed_equal_backing_aft_uv_samples_compared', 'batched_native_draw_samples', 'live_text_samples_compared',
        'render_random_inputs_replayed', 'render_random_inputs_captured', 'unreplayed_render_random_inputs',
        'draw_vibration_scopes_without_native_inputs', 'equivalent_offscreen_culls', 'equivalent_degenerate_culls']
    result = {k: report[k] for k in fields if k in report}
    result['interactive'] = {k: report['interactive'][k] for k in interactive_fields if k in report['interactive']}
    result['error_count'] = len(report['errors'])
    result['mismatch_count'] = len(report['mismatches'])
    result['pending_coverage'] = report['pending_coverage']
    result['pending_coverage_count'] = len(report['pending_coverage'])
    if 'production_replay' in report:
        result['production_replay'] = summarize(report['production_replay'])
    return result

def main(args):
    directory = Path(args.directory).resolve()
    assert directory.is_relative_to(ROOT / 'accepted')
    proof = json.loads((directory / 'acceptance-proof.json').read_bytes())
    download = json.loads((directory / 'packed-download-receipt.json').read_bytes())
    packed = Path(download['path'])
    assert packed.stat().st_size == download['bytes'] and sha(packed) == download['sha256']
    native_path = Path(proof['candidate']['native_evidence'])
    assert sha(native_path) == proof['candidate']['native_evidence_sha256']
    with zipfile.ZipFile(directory / 'accepted-replay-evidence.zip') as archive:
        assert archive.testzip() is None
        raw = archive.read('report.json')
        assert hashlib.sha256(raw).hexdigest() == proof['accepted_report_sha256']
        report = json.loads(raw)
    assert report['archive_accepted'] is True and not report['errors'] and not report['mismatches']
    resources = {}
    with zipfile.ZipFile(native_path) as archive:
        assert archive.testzip() is None
        for stage in ['capture', 'archive']:
            resources[stage] = json.loads(archive.read('stages/' + stage + '/receipt.json'))
    with zipfile.ZipFile(directory / 'pack-evidence.zip') as archive:
        assert archive.testzip() is None
        resources['pack'] = json.loads(archive.read('stages/pack/receipt.json'))
    for stage, receipt in resources.items():
        assert receipt['service_result'] == 'success' and str(receipt['exit_status']) == '0', stage
        observed = receipt['resource_usage']
        assert observed['CPUQuotaPerSecUSec'] == '2s'
        assert int(observed['MemoryMax']) == 6 * 1024**3 and int(observed['MemorySwapMax']) == 0
    destination = directory / 'integration-evidence'
    destination.mkdir(exist_ok=False)
    files = {name: directory / name for name in ['acceptance-proof.json', 'accepted-replay-evidence.zip',
        'pack-evidence.zip', 'pack-evidence-members.json', 'packed-download-receipt.json',
        'pack-execution.json', 'prepared.json']}
    files['native-capture-evidence.zip'] = native_path
    files.update({name: ROOT / name for name in ['pack_accepted.py', 'pack-recipes.json', 'remote_capture.py', 'seal_accepted.py']})
    if proof['case'] == 'sharkmode':
        files.update({name: ROOT / name for name in ['native-capture-evidence-members.json',
            'capture-execution.json', 'download-receipt.json', 'source-and-recipe.json']})
    else:
        original = Path('C:/GitHub/itgmania-harness/target') / (proof['case'] + '-20261120')
        baseline = original / 'baseline-before-fix-evidence.zip'
        assert baseline.is_file()
        files['baseline-before-fix-evidence.zip'] = baseline
    for name, source in files.items():
        raw = source.read_bytes()
        with (destination / name).open('xb') as output:
            output.write(raw)
        assert sha(destination / name) == sha(source)
    coverage = {'case': proof['case'], 'accepted_report_sha256': proof['accepted_report_sha256'],
        'source_commit': proof['source_commit'], 'runner_sha256': proof['runner_sha256'],
        'native_harness_commit': proof['harness_commit'], 'native_harness_sha256': proof['harness_sha256'],
        'capture_counts': proof['native_counts'], 'checks': summarize(report), 'resources': resources}
    write(destination / 'coverage-summary.json', coverage)
    with (destination / 'README.md').open('x', encoding='utf-8') as output:
        output.write('# ' + proof['case'] + ' accepted reference\n\n')
        output.write('The archive preserves the exact fresh native capture accepted by the retained combined production and diagnostic replay. ')
        output.write('Capture and packing used harness commit `' + proof['harness_commit'] + '` and binary SHA `' + proof['harness_sha256'] + '`.\n\n')
        output.write('The passing report is retained completely in `accepted-replay-evidence.zip`, together with its execution receipt, compiled build binding and source proof. ')
        output.write('`coverage-summary.json` records the measured counts, remaining coverage and actual resource receipts. ')
        output.write('The whole-song, production-parity and pixel-parity flags remain false; acceptance covers the checks recorded in that report.\n\n')
        output.write('The packed archive SHA is `' + download['sha256'] + '` and its decoded SHA is `' + download['decoded_sha256'] + '`. ')
        output.write('No native samples or expected values were rewritten. The archive itself is outside this compact evidence directory and bound by `manifest.json`.\n')
    members = {p.name: {'bytes': p.stat().st_size, 'sha256': sha(p)} for p in sorted(destination.iterdir()) if p.is_file()}
    manifest = {'case': proof['case'], 'archive': download, 'accepted_report_sha256': proof['accepted_report_sha256'],
        'source_commit': proof['source_commit'], 'runner_sha256': proof['runner_sha256'], 'members': members,
        'member_count': len(members), 'member_bytes': sum(r['bytes'] for r in members.values()),
        'no_source_or_fixture_mutations': True}
    write(destination / 'manifest.json', manifest)
    print(json.dumps({'sealed': True, 'directory': str(destination), 'manifest_sha256': sha(destination / 'manifest.json'),
        'member_count': len(members), 'member_bytes': manifest['member_bytes'], 'archive_sha256': download['sha256']}), flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', required=True)
    main(parser.parse_args())
