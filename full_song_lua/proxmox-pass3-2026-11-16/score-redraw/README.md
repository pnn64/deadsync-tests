# Gameplay score redraw and formatting parity

The pinned Simply Love score actor now schedules one redraw per player in the gameplay underlay update. A burst of judgments no longer appends a command for every judgment to the score actor’s tween queue. Authored tweens continue, and cancelling that queue cannot strand the pending redraw. The native engine’s tween queue behavior is unchanged.

DeadSync now loads that same score actor and queue helper instead of a static score placeholder, including the separate routine statistics owner. `FormatPercentScore` checks the Lua number, narrows it to native float precision, and uses the native width, rounding and nonfinite formatting contract.

Source commits: DeadSync `077e16fb6cee8726af643160050af3b92c87f212`, harness `0a9a76a3b92ba13f93146ee94aa7515ca0bd601d` (0.1.104), Simply Love `1feda1fd43d96baca951351bb28a35d5e690ebc7`. The native binary is unchanged from the 0.1.103 input-clock build. [Build and validation hashes](validation.json) retain the provenance.

## Fresh controls

| Control | Frames | Capture | Replay | Accepted selector |
| --- | ---: | ---: | ---: | --- |
| [score-format](pass3-score-final-controls/score-format/result.json) | 507 | 11.2s | 3.6s | 3ffb9f893a7f16c8 |
| [score-queue-v2](pass3-score-final-controls/score-queue-v2/result.json) | 507 | 11.6s | 3.5s | d1590685c939b0c4 |
| [score-redraw-manual](pass3-score-final-controls/score-redraw-manual/result.json) | 595 | 13.0s | 3.5s | 6bd09448fb3818c4 |

All three captures use harness 0.1.104. Full replays have zero implemented comparison mismatches or callback errors, compare broadcast parameters and retain every native frame. The manual control verifies 0%, 50% and 100% score text after real inputs, a 75-judgment burst, queue cancellation and an in-progress authored tween. The format control records 16 valid/invalid numeric inputs, padding, hexadecimal strings and nonfinite values.

## Existing fixture regressions

| Fixture | Frames | Replay |
| --- | ---: | ---: |
| [280-MODS-[MASTER] Sharkmode/Sharkmode.ssc](pass3-score-regressions/68eda87bf02562c3/result.json) | 8236 | 28.9s |
| [Sharkmode [Ky_Dash]/Sharkmode.ssc](pass3-score-regressions/730650ffb42269d8/result.json) | 8338 | 29.3s |
| [__pass3_controls/routine-fail/dance/control.ssc](pass3-score-regressions/routine-fail-dance/result.json) | 624 | 3.8s |
| [__pass3_controls/routine-fail/pump/control.ssc](pass3-score-regressions/routine-fail-pump/result.json) | 612 | 3.7s |
| [__pass3_controls/routine-life/dance/control.ssc](pass3-score-regressions/routine-life-dance/result.json) | 625 | 3.7s |
| [__pass3_controls/routine-life/pump/control.ssc](pass3-score-regressions/routine-life-pump/result.json) | 623 | 3.7s |
| [__pass3_controls/routine-manual/dance/control.ssc](pass3-score-regressions/routine-manual-dance/result.json) | 616 | 3.8s |
| [__pass3_controls/routine-manual/pump/control.ssc](pass3-score-regressions/routine-manual-pump/result.json) | 611 | 3.7s |
| [__pass3_controls/styles/dance/control.ssc](pass3-score-regressions/style-dance-routine/result.json) | 417 | 3.5s |
| [__pass3_controls/styles/pump/control.ssc](pass3-score-regressions/style-pump-routine/result.json) | 405 | 3.6s |

All ten retained-archive replays pass with zero mismatches or callback errors. Their original capture versions remain unchanged; they were not recaptured for this regression check.

## Baselines and limits

- The unchanged 75-judgment control failed with native P1Score tween overflow before the theme fix: [baseline](pass3-native-score-queue-v2-baseline/score-queue-v2/result.json). The first probe incorrectly used the Message-suffixed command and exercised no score queue; it is retained as a setup error.
- DeadSync’s original static placeholder produced three comparison mismatches and one Lua error in the manual control: [baseline](pass3-score-redraw-baseline-results/score-redraw-manual/result.json). The first native manual-score test mistakenly used autoplay, which earns no points; that failure is also retained.
- The score test, 77 native-gameplay tests and 215 Linux harness tests pass. The compatibility suite has 16 passes and one existing infinity-formatting failure in `SecondsToMSSMsMs`. The identical actual/expected mismatch reproduces with the pre-score implementation and frozen snapshot: [before/after audit](pass3-score-redraw-compat-audit/audit.json). The missing worker snapshot was restored byte-for-byte. No unrelated expectation was relaxed.
- The 16 obsolete frozen percent-format observations were replaced by explicit native-contract assertions: [snapshot change](score-format-snapshot-update.json). The platform-specific negative-NaN Windows assertion follows the existing formatter contract; a fresh Windows native capture was not performed.
- Native capture logs still contain the existing ScreenEvaluationStage ActorFrameTexture transition error. The gameplay captures complete cleanly, but this transition error is not fixed by the score repair.
- A Dramatic Irony and James have not yet completed new full captures. The reduced control proves the shared score-queue repair, not a complete primary-song pass. Their observation/memory limits remain unresolved. The primary ledger stays at 489 passes and 14 nonpasses, so the all-chart publication gate is unsatisfied.
- These are complete replays of the implemented diagnostic comparisons. Complete rendering and production preparation parity remain unproven.

Raw logs, traces, build failures, setup errors, control inputs and source hashes are retained under this directory and listed in [the evidence manifest](evidence.json).
