import datetime, hashlib, json, pathlib, re, shutil

WORK = pathlib.Path(__file__).resolve().parent
STORE = pathlib.Path('C:/GitHub/deadsync/tests/fixtures/full_song_lua')
REPORT = STORE / 'proxmox-pass3-2026-11-16'
COLLECTED = WORK / 'score-redraw-collected'
OUT = REPORT / 'score-redraw'
OUT.mkdir(exist_ok=True)

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

evidence = read(COLLECTED / 'manifest.json')
for item in evidence:
    source = COLLECTED / item['local']
    assert source.stat().st_size == item['bytes'] and sha(source) == item['sha256']
    target = OUT / item['local']
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    assert sha(target) == item['sha256']
for name in ['score-format-snapshot-update.json', 'score-code-commit.json',
             'score-native-final-validation.json', 'score-final-validation.json']:
    shutil.copy2(WORK / name, OUT / name)
write(OUT / 'evidence.json', evidence)

fresh = [read(p) for p in sorted((OUT / 'pass3-score-final-controls').glob('*/result.json'))]
regressions = [read(p) for p in sorted((OUT / 'pass3-score-regressions').glob('*/result.json'))]
assert len(fresh) == 3 and len(regressions) == 10
for result in fresh + regressions:
    c = result['comparison']
    assert result['status'] == 'pass' and c['archive_accepted']
    assert c['native_frames'] == c['replayed_frames'] > 0 and c['mismatch_count'] == c['error_count'] == 0
code = read(WORK / 'score-code-commit.json')
proof = read(OUT / 'pass3-score-redraw-build-final/build-proof.json')
oracle = read(OUT / 'pass3-score-harness-final/build-proof.json')
summary = {'recorded_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'deadsync_commit': code['commit'], 'harness_commit': oracle['harness_commit'],
           'harness_version': '0.1.104', 'theme_commit': oracle['theme_commit'],
           'runner_sha256': proof['runner_sha256'], 'harness_binary_sha256': oracle['harness_binary_sha256'],
           'native_binary_sha256': oracle['native_binary_sha256'],
           'fresh_controls': len(fresh), 'retained_archive_regressions': len(regressions),
           'tests': {'score': 1, 'native_gameplay': 77, 'harness_linux': 215, 'harness_ignored': 5,
                     'compatibility_passed': 16, 'compatibility_failed': 1},
           'compatibility_failure': proof['known_unrelated_compatibility_failure'],
           'primary_passes': 489, 'primary_nonpasses': 14, 'all_chart_gate_satisfied': False,
           'results': [{'id': r['id'], 'status': r['status'], 'frames': r['comparison']['replayed_frames'],
                        'replay_seconds': r['stages']['replay']['elapsed_seconds']} for r in fresh + regressions]}
write(OUT / 'validation.json', summary)

lines = ['# Gameplay score redraw and formatting parity', '',
    'The pinned Simply Love score actor now schedules one redraw per player in the gameplay underlay update. A burst of judgments no longer appends a command for every judgment to the score actor’s tween queue. Authored tweens continue, and cancelling that queue cannot strand the pending redraw. The native engine’s tween queue behavior is unchanged.', '',
    'DeadSync now loads that same score actor and queue helper instead of a static score placeholder, including the separate routine statistics owner. `FormatPercentScore` checks the Lua number, narrows it to native float precision, and uses the native width, rounding and nonfinite formatting contract.', '',
    f'Source commits: DeadSync `{code["commit"]}`, harness `{oracle["harness_commit"]}` (0.1.104), Simply Love `{oracle["theme_commit"]}`. The native binary is unchanged from the 0.1.103 input-clock build. [Build and validation hashes](validation.json) retain the provenance.', '',
    '## Fresh controls', '', '| Control | Frames | Capture | Replay | Accepted selector |',
    '| --- | ---: | ---: | ---: | --- |']
for r in fresh:
    lines.append(f'| [{r["id"]}](pass3-score-final-controls/{r["id"]}/result.json) | {r["comparison"]["replayed_frames"]} | {r["stages"]["capture"]["elapsed_seconds"]:.1f}s | {r["stages"]["replay"]["elapsed_seconds"]:.1f}s | {r["accepted_artifact"]["sha256"][:16]} |')
lines += ['', 'All three captures use harness 0.1.104. Full replays have zero implemented comparison mismatches or callback errors, compare broadcast parameters and retain every native frame. The manual control verifies 0%, 50% and 100% score text after real inputs, a 75-judgment burst, queue cancellation and an in-progress authored tween. The format control records 16 valid/invalid numeric inputs, padding, hexadecimal strings and nonfinite values.', '',
    '## Existing fixture regressions', '', '| Fixture | Frames | Replay |', '| --- | ---: | ---: |']
for r in regressions:
    lines.append(f'| [{r["source_simfile"]}](pass3-score-regressions/{r["id"]}/result.json) | {r["comparison"]["replayed_frames"]} | {r["stages"]["replay"]["elapsed_seconds"]:.1f}s |')
lines += ['', 'All ten retained-archive replays pass with zero mismatches or callback errors. Their original capture versions remain unchanged; they were not recaptured for this regression check.', '',
    '## Baselines and limits', '',
    '- The unchanged 75-judgment control failed with native P1Score tween overflow before the theme fix: [baseline](pass3-native-score-queue-v2-baseline/score-queue-v2/result.json). The first probe incorrectly used the Message-suffixed command and exercised no score queue; it is retained as a setup error.',
    '- DeadSync’s original static placeholder produced three comparison mismatches and one Lua error in the manual control: [baseline](pass3-score-redraw-baseline-results/score-redraw-manual/result.json). The first native manual-score test mistakenly used autoplay, which earns no points; that failure is also retained.',
    '- The score test, 77 native-gameplay tests and 215 Linux harness tests pass. The compatibility suite has 16 passes and one existing infinity-formatting failure in `SecondsToMSSMsMs`. The identical actual/expected mismatch reproduces with the pre-score implementation and frozen snapshot: [before/after audit](pass3-score-redraw-compat-audit/audit.json). The missing worker snapshot was restored byte-for-byte. No unrelated expectation was relaxed.',
    '- The 16 obsolete frozen percent-format observations were replaced by explicit native-contract assertions: [snapshot change](score-format-snapshot-update.json). The platform-specific negative-NaN Windows assertion follows the existing formatter contract; a fresh Windows native capture was not performed.',
    '- Native capture logs still contain the existing ScreenEvaluationStage ActorFrameTexture transition error. The gameplay captures complete cleanly, but this transition error is not fixed by the score repair.',
    '- A Dramatic Irony and James have not yet completed new full captures. The reduced control proves the shared score-queue repair, not a complete primary-song pass. Their observation/memory limits remain unresolved. The primary ledger stays at 489 passes and 14 nonpasses, so the all-chart publication gate is unsatisfied.',
    '- These are complete replays of the implemented diagnostic comparisons. Complete rendering and production preparation parity remain unproven.', '',
    'Raw logs, traces, build failures, setup errors, control inputs and source hashes are retained under this directory and listed in [the evidence manifest](evidence.json).', '']
(OUT / 'README.md').write_text('\n'.join(lines), encoding='utf-8')

p = REPORT / 'README.md'
text = p.read_text(encoding='utf-8')
bullet = '- Gameplay scores now use the real theme actor in DeadSync, native percent formatting, and a deferred redraw queue in the pinned theme. Three fresh harness 0.1.104 score controls and all ten routine/Sharkmode regressions pass full replays. The reduced native overflow baseline fails before the theme repair; the full A Dramatic Irony/James cases remain unproven. The [score report](score-redraw/README.md) retains original failures, source pins, the existing compatibility-test failure, and transition-error limits. The primary ledger remains 489 passes / 14 nonpasses.'
assert bullet not in text
text = text.replace('## Completed repairs and checks\n\n', '## Completed repairs and checks\n\n' + bullet + '\n\n', 1)
p.write_text(text, encoding='utf-8')

timing = ['<!-- score-redraw-runtimes:start -->', '## Score redraw and formatting controls', '',
    'These are saved measurements from the score parity validation, not new runs made for this guide. The three fresh 0.1.104 controls passed on the eight-vCPU worker. Replay excludes builds and decompression; the configured replay cap was 6 GiB.', '',
    '| Control | Replay | Native capture | Accepted archive selector |', '| --- | ---: | ---: | --- |']
for r in fresh:
    timing.append(f'| {r["id"]} | {r["stages"]["replay"]["elapsed_seconds"]:.1f}s | {r["stages"]["capture"]["elapsed_seconds"]:.1f}s | {r["accepted_artifact"]["sha256"][:16]} |')
timing += ['', 'Use `score-redraw-manual` for score text, deferred updates and authored tween interactions; `score-queue-v2` for judgment bursts; and `score-format` for numeric conversion and formatting. See the [full evidence and coverage limits](proxmox-pass3-2026-11-16/score-redraw/README.md).', '',
    '```powershell', 'cargo test --release --test full_song_lua -- --jobs 1 ' + ' '.join(r['accepted_artifact']['sha256'][:16] for r in fresh), '```', '<!-- score-redraw-runtimes:end -->', '']
p = STORE / 'fixture-runtimes.md'
text = p.read_text(encoding='utf-8')
assert '<!-- score-redraw-runtimes:start -->' not in text
text = text.replace('## Choosing what to run', '\n'.join(timing) + '\n## Choosing what to run', 1)
p.write_text(text, encoding='utf-8')
print(json.dumps(summary))
