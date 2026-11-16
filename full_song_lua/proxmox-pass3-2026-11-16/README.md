# Song Lua parity pass 3

Status: **in progress**. This report records completed evidence from the replacement fleet; it does not claim a fresh full-corpus pass.

## Completed repairs and checks

- Gameplay scores now use the real theme actor in DeadSync, native percent formatting, and a deferred redraw queue in the pinned theme. Three fresh harness 0.1.104 score controls and all ten routine/Sharkmode regressions pass full replays. The reduced native overflow baseline fails before the theme repair; the full A Dramatic Irony/James cases remain unproven. The [score report](score-redraw/README.md) retains original failures, source pins, the existing compatibility-test failure, and transition-error limits. The primary ledger remains 489 passes / 14 nonpasses.

- Routine team statistics now use an independent ordered scorekeeper, failed flag and Lua object. Both formerly failing manual controls and both fresh failure-isolation controls pass; the four life/style controls and both Sharkmode variants also pass complete replays with zero mismatches or Lua errors. Selected suites pass 846 gameplay, 11 statistics and 77 native gameplay tests. The [routine statistics report](routine-stats-replays/README.md) retains original failures, fixed observer coverage and source provenance. Four new accepted controls are published. The primary ledger remains 489 passes / 14 nonpasses; the all-chart gate remains open.

- Routine shared life now matches the native object identity, immediate writes and separate participant histories. Both life probes and both routine autoplay controls pass complete replays with zero mismatches/errors. At the life-repair baseline, manual dance/pump controls dropped from 46 to 18 mismatches, with life comparisons resolved; the then-missing `GetRoutineStageStats` is now implemented as described above. All 844 gameplay tests pass. The broad semantic suite has 302 passes, 9 failures and 94 ignored tests: missing archive setup accounts for eight, and the same six glow numeric mismatches reproduce before the patch. The [routine-life report](routine-life-replays/README.md) and [validation record](routine-life-validation.json) retain the full evidence. Four accepted supplemental archives are published; the 503-primary ledger and all-chart gate are unchanged.

- Recorded physical inputs now enter production gameplay routing before Lua callbacks, using the native step clocks. The two focused tests and all 75 gameplay regression tests pass. At the input-repair baseline, both manual routine replays had 46 mismatches instead of the historical 82: compared points, W1 and misses agreed; recorded life and missing `GetRoutineStageStats` remained at that stage. [Input validation](input-routing-validation.json) and [replay details](input-routing-replays/README.md) retain the complete failures. Two fresh [native routine-life controls](native-validation/pass3-routine-life/README.md) isolate shared meter identity, immediate writes and independent history; their [DeadSync baselines](routine-life-baselines/README.md) each have 32 mismatches and no callback errors.

- Harness 0.1.103 retains the original native input judgment clock reads, which the later Lua event timestamp cannot recover. All 216 Windows and 215 Linux harness tests pass, along with the native press/release regression. Two fresh [routine input-clock captures](routine-manual-input-clocks/README.md) preserve both players' clocks and unchanged native scores. These input-clock captures are native references; the subsequent DeadSync input, life and routine-statistics repairs are recorded above. See [validation and hashes](input-clock-validation.json).

- Inactive-player startup input: harness 0.1.99 configures and captures both sides before authored Lua joins P2. DeadSync consumes the declared input and checks theme initialization only for initially enabled sides.
- Fresh Anxiety SM and SSC captures plus the inactive-player join/reload control replay with zero implemented comparison mismatches and no callback errors.
- ArrowQuest rechecks use the retained, hash-verified native captures in a 96 GiB VM with an 84 GiB process cap. Their individual records distinguish completed replays from work still running.
- After Dark roll-clock handling tracks previously active roll heads and uses the current rounded song row across clock rewinds. The retained full capture passes with zero mismatches, down from 175; fresh recapture results are recorded separately.
- A reduced probe against ITGmania’s bundled Lua confirms that GC retires deleted collectable keys, even when their objects remain alive elsewhere. The DeadSync fix passes the native order/cursor probe and 249 selected library, GC, table and allocation checks; both fresh KENPO references still have seven mismatches, and fresh automatic-GC Velvet repetitions still have 17,872 and 20,688 mismatches.
- Fresh Megalovania passes with the existing roll/input/GC runner before the new pause patch. This does not establish the cause of its previous six mismatches. The longer-lived pause control independently reproduced missing Pause/Unpause commands and incorrect return values before the pause fix (2,015 mismatches).
- KENPO native repetitions retain the exact ordering comparison; events are not sorted to obtain a pass. The fresh stopped-GC control passes with zero mismatches, narrowing the remaining gap to GC-sensitive table ordering. This supplemental profile does not replace the automatic-GC primary case.
- Pause integration now connects Lua transitions to audio consumption and gameplay judgments, preserves actor/sound-effect updates, and dispatches native Pause/Unpause commands with no return values. The [validation record](pause-unit-validation.json) includes 1,009 passing Linux tests and the completed native control: all 1,106 frames replay with zero implemented comparison mismatches or callback errors. The five additional replays (Megalovania, both Anxiety formats, join/reload and After Dark) also pass. Broader operation/rendering coverage remains explicitly unproven. The original setup-only failure is retained: nine pinned expectation files were restored before resuming the checks.

- Harness 0.1.100 adds an explicit native chart index and game selection, preserving the launch identity and catalog. Its 216 normal tests pass. The Windows native selector control (native revision 704cdd5) and pinned Linux native control (008bfcf) pass with an explicitly valid pump noteskin. The original missing-noteskin failure is retained. DeadSync exact-chart/game/style selection passes on both platforms; [selection validation](chart-selection-validation.json) and [Linux source validation](style-selector-linux-validation.json) record the evidence. Published captures retain their individual 0.1.99 or 0.1.100 versions. This is preparation for the all-chart pass, not an all-chart coverage claim.

- The twelve fresh selector/style controls completed: six pass (SM/SSC second Edit selection and dance single/versus/double/couple). Three clean pump references exposed the production style handoff failure; pump couple and both routine styles exposed native theme errors. See the [style validation record](native-style-validation.json). Subsequent targeted replays are recorded separately below and do not erase the original failures.

- Pump single, versus and double now complete full replays with zero mismatches or callback errors. DeadSync preserves the pump game while resolving bare styles, and gameplay handoff accepts the retained pump-qualified style. The handoff-only intermediate replay had one game metadata mismatch in each case. [Game metadata validation](pump-game-validation.json) and [handoff validation](pump-style-validation.json) retain both steps. Linux GameState tests pass 15/15 after restoring the exact published snapshot; the stale expectation failure is retained separately.

- Harness 0.1.101 fixes input observation when no Lua input callback is registered. Its regression fails against the old binary and passes after the observer moves to native screen dispatch, without duplicate callback observations or altered scoring. See [input observer validation](input-observer-validation.json).

- Harness 0.1.102 pins the published native routine ownership/scoring/noteskin backports and the pump couple theme width fix. [Validation](oracle-pins-validation.json) records 216 Windows tests, 215 Linux tests, native input and chart-selector checks, and two manual routine captures with all eight input events. The team combo resets on the intentional P2 miss before the next P1 success. The original [twelve native controls](native-routine-first-results.json) are retained separately.

- At the earlier routine baseline, five fresh or retained 0.1.102 controls were replayed: pump couple passes with zero mismatches/errors; dance and pump routine each have 20 recorded-life mismatches; both manual routine cases have 82 mismatches and two missing GetRoutineStageStats errors. At this baseline, the replay input dispatcher forwarded observations only to Lua, so manual scoring differences also expose a test-runner input-routing gap. These four failures are supplemental controls, outside the 503-primary ledger. See the [routine baseline summary](routine-baseline-summary.json) and [native-only manual controls](routine-manual-controls/README.md).

## Latest available primary ledger

| Result | Cases |
| --- | ---: |
| capture_observation_limit | 1 |
| capture_resource_limit | 1 |
| native_capture_error | 1 |
| native_lua_error | 8 |
| no_selectable_chart | 1 |
| parity_failure | 2 |
| pass | 489 |

The [case ledger](case-ledger.json) carries historical results forward explicitly. [Current failures](current-failures.json) retain the missing behavior or evidence for every nonpassing primary case.

## Fleet and profiling

All 34 old task VMs (1200–1216 and 1300–1316) were removed from Proxmox after retaining their disks and configuration evidence. The replacement template is 1400; workers 1401–1415 have two vCPUs each and are started only within the host memory budget. Retained disk chains are independent of the deleted VM registrations.

All six heavy-fixture profiles completed on VM 1415 using samply at 99 Hz: two repeated replays each of Mr Sandman, Paint SSC and fof, all with passing diagnostic comparisons. The baseline runner includes debug information and frame pointers. Completed profiles and symbol sidecars are retained before analysis; no performance optimization is part of this pass.

Worker 1415 is stopped after profiling. Worker 1402 was restarted and temporarily assigned eight vCPUs and 16 GiB for the isolated native build and controls. Worker 1414 has a [recorded 160 GiB allocation](james-resource-setup.json) and a 148 GiB capture cap. The James SM capture child was OOM-killed after about 1h 40m. Diagnostic preservation is complete, and the [1.40 GB compressed archive](james-terminal-retention.json) has been SHA-256 verified locally and on the guest. The [raw native metadata](james-65m-native-metadata.json) reaches gameplay exit but records 12,264,875 dropped events beyond the 65-million-event budget, four P1Score tween overflows and a transition AFT error. It cannot be accepted as a clean reference. Its disk was [expanded to 256 GiB](james-diagnostics-disk-growth.json) to retain the large diagnostics. [Worker 1414 is now stopped](james-worker-shutdown.json); no unchanged recapture was started.

## Scope and reproducibility

A pass means a full replay of the implemented diagnostic comparisons. Reports explicitly leave production preparation, unsupported operations, subscriber identity and complete rendering parity unproven. No corpus Lua source or authored simfile was edited to obtain these results.

The all-chart gate is still open: the source-header inventory contains **1,461 chart headers across 503 simfiles**, including **84 duplicate type/difficulty selections**. It has not yet been validated against the native loader. The prior primary sweeps selected one chart/profile per simfile and do not satisfy all-chart coverage.

See [native attempts](native-attempts.json), [replays](replays.json), [ArrowQuest resource replays](arrow-resource-replays.json), [published archives](published-archives.json), and [source revisions](repository-pins.json). Completed reports and full profiling artifacts are also retained under the local pass-three work directory and on the named workers.

Completed profiling artifacts and comparisons: [CPU profile report](profiles/README.md).
