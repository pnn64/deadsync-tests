# Routine shared-life repair

The physical meter and the individual recorded history are separate native objects. In routine mode, both `ScreenGameplay:GetLifeMeter` calls return the same `CoopLifeMeterInternal` under `CombinedLife`. A participant write changes that meter immediately. Each `PlayerStageStats` keeps its own history; `Player::ChangeLifeRecord` reads the independent tug-life value (initially 0.5) instead of the inner meter. Empty history returns 0. The fix models these distinctions in gameplay and the Lua bindings.

Native source: `Player.cpp` (Load and ChangeLifeRecord), `CombinedLifeMeterShared.cpp`, and `ScreenGameplay.cpp` (GetLifeMeter), revision `663525dcb86eb570d0ef6a2e209678436660ae26`. The [native life probes](../native-validation/pass3-routine-life/README.md) and [failing baselines](../routine-life-baselines/README.md) are retained unchanged.

| Control | Native harness | Before | After | Callback errors | Frames replayed |
| --- | --- | ---: | ---: | ---: | ---: |
| [routine-life-dance](routine-life-dance/result.json) | 0.1.103 | 32 | 0 | 0 | 625 / 625 |
| [routine-life-pump](routine-life-pump/result.json) | 0.1.103 | 32 | 0 | 0 | 623 / 623 |
| [routine-manual-dance](routine-manual-dance/result.json) | 0.1.103 | 46 | 18 | 2 | 616 / 616 |
| [routine-manual-pump](routine-manual-pump/result.json) | 0.1.103 | 46 | 18 | 2 | 611 / 611 |
| [style-dance-routine](style-dance-routine/result.json) | 0.1.102 | 20 | 0 | 0 | 417 / 417 |
| [style-pump-routine](style-pump-routine/result.json) | 0.1.102 | 20 | 0 | 0 | 405 / 405 |

All six replays use the exact retained native candidate bytes, verified by their decoded SHA-256. No authored source, profile, tolerance, comparison ordering or reference output was changed. The two life probes retain harness 0.1.103 captures; the autoplay style probes retain 0.1.102. The current 0.1.103 packer preserves each archive's original capture version.

The four passing controls are published as accepted archives. Both manual-input controls remain unaccepted: each has 16 query-event mismatches, one query-count mismatch and one broadcast-count mismatch, plus two missing `GetRoutineStageStats` errors. All compared life fields now agree. Separate ordered team statistics are still required; sharing a player table or summing current combos would not match the native team scorekeeper.

Validation: all 844 gameplay library tests pass. The broad Lua semantic suite has 302 passes, 9 failures and 94 ignored tests. Eight failures require absent full-song archives or follow a poisoned fixture cache. `short_glow_matches_native` has the same six numeric mismatches before and after this patch; that separate gap remains open. See the [validation record](../routine-life-validation.json), [full test log](../native-validation/pass3-routine-life-fix/semantic-tests.log), [fixture inventory](../native-validation/pass3-routine-life-fix/fixture-availability.json) and [glow baseline comparison](../native-validation/pass3-routine-life-fix/glow-baseline-validation.json). The broad suite is not green.

These are supplemental controls. The primary ledger remains 489 passes / 14 nonpasses. Full production preparation and complete rendering parity remain unproven, and the all-chart publication gate is not satisfied.
