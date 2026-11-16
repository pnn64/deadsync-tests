# Routine team-statistics repair

Routine now owns a secondary scorekeeper, updated in participant event order after each primary scorekeeper. Its points, judgment counts, combo and failed flag are independent of P1 and P2. Lua exposes a stable, separate `GetRoutineStageStats` object through both statistics feed paths. Participant `MaxCombo` tracks recorded combos; the team keeps no combo history, matching native behavior.

The new failure-isolation controls fail P1 before the first inputs, then fail the team after its first two hits. Native P1 finishes with zero earned points, P2 with -2, and the team with 10 of 25 possible points. Team counts and combo continue after its earned score freezes. Both games retain five judgment callbacks and all eight physical input events. See the [native controls](../routine-fail-controls/README.md).

Native source: `StageStats.cpp`, `ScreenGameplay.cpp`, `ScoreKeeperShared.cpp`, `ScoreKeeperNormal.cpp`, `Player.cpp` and `PlayerStageStats.cpp`, revision `663525dcb86eb570d0ef6a2e209678436660ae26`.

| Fixture | Native harness | Frames replayed | Mismatches | Lua errors | Replay |
| --- | --- | ---: | ---: | ---: | ---: |
| [280-MODS-[MASTER] Sharkmode/Sharkmode.ssc](68eda87bf02562c3/result.json) | 0.1.98 | 8236 / 8236 | 0 | 0 | 28.3s |
| [Sharkmode [Ky_Dash]/Sharkmode.ssc](730650ffb42269d8/result.json) | 0.1.98 | 8338 / 8338 | 0 | 0 | 28.7s |
| [__pass3_controls/routine-fail/dance/control.ssc](routine-fail-dance/result.json) | 0.1.103 | 624 / 624 | 0 | 0 | 3.3s |
| [__pass3_controls/routine-fail/pump/control.ssc](routine-fail-pump/result.json) | 0.1.103 | 612 / 612 | 0 | 0 | 3.5s |
| [__pass3_controls/routine-life/dance/control.ssc](routine-life-dance/result.json) | 0.1.103 | 625 / 625 | 0 | 0 | 3.5s |
| [__pass3_controls/routine-life/pump/control.ssc](routine-life-pump/result.json) | 0.1.103 | 623 / 623 | 0 | 0 | 3.7s |
| [__pass3_controls/routine-manual/dance/control.ssc](routine-manual-dance/result.json) | 0.1.103 | 616 / 616 | 0 | 0 | 3.6s |
| [__pass3_controls/routine-manual/pump/control.ssc](routine-manual-pump/result.json) | 0.1.103 | 611 / 611 | 0 | 0 | 3.5s |
| [__pass3_controls/styles/dance/control.ssc](style-dance-routine/result.json) | 0.1.102 | 417 / 417 | 0 | 0 | 3.6s |
| [__pass3_controls/styles/pump/control.ssc](style-pump-routine/result.json) | 0.1.102 | 405 / 405 | 0 | 0 | 3.6s |

The first implementation matched all source broadcast parameters and stage fields, but the observer wrapped only participant point getters. The [initial manual replay](../routine-stats-baseline-replays/routine-manual-dance/result.json) had 46 query mismatches and no Lua errors; the [initial failure control](../routine-stats-baseline-replays/routine-fail-dance/result.json) had 74. The observer now records the same point getters on the independent team object. A regression test checks both getters for P1, P2 and the team across two live updates. Comparison order, tolerances and native traces were not changed.

Validation: 846 gameplay tests, 11 statistics tests, and 77 native gameplay tests pass. [Validation and source hashes](../routine-stats-validation.json) link the tested runner to commit `9ab5cdc0e1d9e4f1af83b78a7099be910d7a57e9`. The initial compile error, missing worker snapshots, API snapshot update, and observer-test setup correction remain in [build evidence](../native-validation/pass3-routine-stats-fix/source-proof.json) and subsequent validation directories. Only the new API/private-field key lists changed in the [statistics snapshot](../native-validation/pass3-routine-stats-fix/statistics-snapshot-update.json); numeric expectations were preserved.

Four newly accepted archives are published: manual dance/pump and failure-isolation dance/pump. The four life/style controls and both Sharkmode references reuse already accepted archives. Native capture versions remain explicit: 0.1.103 for manual, failure and life controls; 0.1.102 for routine autoplay styles; 0.1.98 for Sharkmode. The current 0.1.103 packer preserves original capture provenance.

These results prove full replay of the implemented diagnostic comparisons. Production preparation and complete rendering remain outside that claim. The complete semantic suite was not rerun; its previously documented fixture-availability and glow-precision issues remain open. The primary ledger remains 489 passes / 14 nonpasses. The two manual routine supplemental failures are resolved; the all-chart publication gate is still unsatisfied.

Independent team course-history carry, the full native combo-list API and additional score/statistics APIs are not established by these single-song controls.
