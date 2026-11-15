# Song Lua parity repair pass

Status: **complete**. This pass targets the 59 non-passing primary cases from the 503-case audit, two Sharkmode regressions, Sequential Dreambox, and six alternate-profile controls. Additional reduced native controls isolate observer, reload, and feedback behavior.

Fresh primary cases recorded: **62**. Historical primary cases not rerun: **441**. The latest-available 503-case ledger is **not** a fresh full-corpus result for this revision.

| Latest available primary result | Cases |
| --- | ---: |
| capture_observation_limit | 2 |
| native_capture_error | 1 |
| native_lua_error | 10 |
| no_selectable_chart | 1 |
| parity_failure | 4 |
| pass | 483 |
| replay_resource_limit | 2 |

Previously non-passing primary cases now passing: **40 of 59**. Previously passing primary cases now rejected: **1**. This includes the newly observed native syntax failure in Sequential Dreambox.

## Fresh primary results

| Fresh result | Cases |
| --- | ---: |
| capture_observation_limit | 2 |
| native_capture_error | 1 |
| native_lua_error | 10 |
| no_selectable_chart | 1 |
| parity_failure | 4 |
| pass | 42 |
| replay_resource_limit | 2 |

## Repairs and evidence

- DeadSync: classify lowercase `getaux` as a query; initialize effect clocks before the first update; preserve logical background entrypoint spelling; carry joined-player roster/style/positions through gameplay reload; observe newly returned style objects; preserve BackgroundEffect wrapper paths for subscribers; drain autoplay rolls using the native frame delta.
- RSSP `5b0284eed201e6511265f9e295e3520e12ac1536` (0.4.291): retain inline measure delimiters when parsing note rows. Ultimate now has the complete chart rather than a one-measure parse.
- Harness: preserve fluent PlayerOptions/SongOptions return identity, record LastSeenVideoDriver, observe native Lua load/runtime/tween failures, isolate post-gameplay transition errors, retain crash diagnostics, and reduce avoidable JSON/file copies. Imported traces with observed script errors are rejected too.
- Native ITGmania `008bfcfef57a107eaafe08b4de7d9d42c6dd1e2f`: pad movie surfaces for SIMD color conversion while retaining logical dimensions. Five movie controls have zero Valgrind errors; fresh full-song cases test the formerly crashing videos.
- New native controls cover initial clocks, fluent options, preferences, malformed source rejection, join/reload, and feedback clocks. The final join control verifies both player positions and style queries. A roll control using a fixed 0.2-second update delta passes; the real-song captures provide the irregular-frame regression evidence.
- The manual-player native golden is refreshed from the native oracle. The harness projection had 171 decimal-only differences, all with identical float32 bits. The full DeadSync fixture already had the same numeric values. Exact geometry comparisons remain enabled.

## Reproducibility and limits

The 15 fresh workers are VMs 1301–1315 with two CPUs each; 1316 is a temporary four-CPU build/control helper. Resource retries raise individual budgets from 6 GiB to 26, 42, or 50 GiB. Complete command lines, event caps, timeouts, native profiles, hashes, and failed attempts are retained in the JSON records. The old fleet and all disks remain available.

Native captures use the new harness/native source snapshot. Later DeadSync fixes replay those exact, hash-verified fresh captures. `final-replays.json` records the final runner SHA and its source snapshot separately from the capture snapshot; earlier results are not relabeled as final. The source diff includes seven pre-existing user edits to actor capture boxing, preserved separately and excluded from the DeadSync repair commit.

One host-wide memory exhaustion killed VM 1314 after the native raw trace was published, during capture postprocessing. Finished workers were shut down; the completed raw trace was hash-verified and checked for clean gameplay exit, zero drops/errors, null renderer, and the expected native revision. Recovery uses the existing song-lua-analyze command with the two provenance assignments normally made by capture_in (source_simfile and command_observer). Archive and replay validation remain enabled; the original raw trace is retained. This is an infrastructure interruption, not a song verdict. An initial final-replay helper used a non-content-addressed filename; those rejected attempts are retained and repeated with the correct archive name.

Pass means all implemented diagnostic comparisons succeeded. Production preparation and complete rendering parity remain unproven. The original audit’s XML/entrypoint/profile guards and zero-actor coverage limits still apply to historical cases. No comparator tolerance, event ordering, corpus Lua source, or authored simfile was changed to obtain a pass.

Committed source and dependency revisions are recorded in [repository pins](repository-pins.json). Targeted DeadSync checks, the complete harness test suite, and RSSP tests passed; [local validation](local-validation.json) records their counts and ignored tests. The entire DeadSync application test suite was not rerun.

## Current primary failures

| Song simfile | Status | Mismatches | Missing behavior or evidence |
| --- | --- | ---: | --- |
| 242-MISC.[lv.02] ChikuTaku/ChikuTaku.ssc | native_lua_error | - | Authored native movie setup passes a nil musicrate to Sprite.rate. Supply/resolve the song dependency before accepting a native oracle. |
| 308-MISC-[lv.Quest] [Tech Spectrum Super - _TRUE GAMERS CLICK HERE - EXTRA CHARTS]/ArrowQuest.sm | replay_resource_limit | - | No complete comparison under the recorded resource/observation limits. Streaming trace parsing/replay or a larger isolated budget is still needed; do not infer a semantic verdict. Limits: {"capture":{"memory_limit":"50G","timeout_seconds":900,"elapsed_seconds":200.589,"exit":0},"archive":{"memory_limit":"50G","timeout_seconds":600,"elapsed_seconds":348.394,"exit":0},"replay":{"memory_limit":"50G","timeout_seconds":3600,"elapsed_seconds":1378.499,"exit":1}} |
| 308-MISC-[lv.Quest] [Tech Spectrum Super]/ArrowQuest.sm | replay_resource_limit | - | No complete comparison under the recorded resource/observation limits. Streaming trace parsing/replay or a larger isolated budget is still needed; do not infer a semantic verdict. Limits: {"capture":{"memory_limit":"50G","timeout_seconds":4290,"elapsed_seconds":2763.625,"exit":0},"archive":{"memory_limit":"50G","timeout_seconds":600,"elapsed_seconds":344.832,"exit":0},"replay":{"memory_limit":"50G","timeout_seconds":3600,"elapsed_seconds":1428.093,"exit":1}} |
| [11] KENPO SAITO (DX) [Scrypts]/KENPO SAITO-chart.ssc | parity_failure | 7 | Seven same-frame node-order differences remain. Preserve native traversal/table allocation order; see the first-audit permutation proof. No comparator sorting was added. |
| [FULL SONG] ChikuTaku [wrsw]/ChikuTaku.ssc | native_lua_error | - | Authored native movie setup passes a nil musicrate to Sprite.rate. Supply/resolve the song dependency before accepting a native oracle. |
| A Dramatic Irony/A Dramatic Irony.ssc | native_lua_error | - | Native reports Tween overflow: "&lt;type 20ScreenGameplayNormal&gt; ScreenGameplay/&lt;type 28ActorFrameAutoDeleteChildren&gt; Underlay/&lt;type 10BitmapText&gt; P1Score"; infinitely recursing ActorCommand?. A clean native run is required before accepting a fixture. |
| After Dark/After Dark.ssc | parity_failure | 175 | The roll frame-clock fix removes 1,065 of 1,240 differences in the same fresh capture. The remaining 175 are a subset of the original mismatches: hold-feedback timing near beat 479.657, with native HoldJudgment time 0.711258 seconds versus DeadSync 0.8. Hold-tail feedback dispatch/frame ordering still needs alignment. |
| Anxiety/Anxiety.sm | native_lua_error | - | The P1-to-versus join/reload control now passes, including roster, style, and positions. This authored native run fails in Simply Love TrackFailTime.lua:121 after P2 joins without autoplay/stream metrics. A clean native reference and a complete inactive-player profile are still needed. Unjoin and physical-P2-origin joins are not established. |
| Anxiety/Anxiety.ssc | native_lua_error | - | The P1-to-versus join/reload control now passes, including roster, style, and positions. This authored native run fails in Simply Love TrackFailTime.lua:121 after P2 joins without autoplay/stream metrics. A clean native reference and a complete inactive-player profile are still needed. Unjoin and physical-P2-origin joins are not established. |
| Bank Account/Bank Account.ssc | native_lua_error | - | The single-player profile accesses an absent PlayerP2. A separate versus capture passes; it does not replace this primary profile. |
| Cursed Metamorph - [Zaia]/saved/Cursed Metamorph.ssc | native_capture_error | - | The saved chart is missing its music dependency; the native capture never yields a valid completed reference. |
| DS ULTIMATE LUA TEST/DS ULTIMATE LUA TEST.sm | native_lua_error | - | Inline-comma parsing is fixed in RSSP, and BackgroundEffect subscriber paths are fixed. Native now reports an overlay.lua tween overflow, including with a fixed 1/60-second update delta; this prevents accepting a complete clean oracle. |
| Happiness/Happiness.ssc | native_lua_error | - | Native diva.lua:1092 reads an exhausted break-length table after foreground restart. Resolve the authored lifecycle error before accepting a native oracle. |
| Haxo (Sharks Remix) [sorae]/haxo.ssc | native_lua_error | - | Authored native effectmagnitude call has too few numeric arguments; the song needs a valid native execution before comparison. |
| james/james.sm | capture_observation_limit | - | Native reaches gameplay exit but the bounded trace loses observations: [{"dropped_events": 41824750}]. A streaming capture/replay path and a sufficient observation budget are needed; the truncated trace is rejected. |
| james/james.ssc | capture_observation_limit | - | Native reaches gameplay exit but the bounded trace loses observations: [{"dropped_events": 41801125}]. A streaming capture/replay path and a sufficient observation budget are needed; the truncated trace is rejected. |
| Lesson by DJ/Lesson by DJ.sm | no_selectable_chart | - | The source SM has no selectable chart (malformed NOTES header). Repair the corpus simfile before a full native run. |
| Megalovania SM5 - [TaroNuke]/megalovania.sm | parity_failure | 6 | ScreenGameplay:PauseGame currently records a Lua flag but does not pause the gameplay/audio runtime. Native Player::Update advances actor children and then skips judgments while paused; descendant Judgment timing diverges around the authored pause. |
| Sequential Dreambox - [Zaia]/Sequential Dreambox.ssc | native_lua_error | - | New native script-error observation exposes FastEnd.lua:47: '&lt;eof&gt;' expected near 'local'. The original zero-Lua-call pass was invalid; the authored script needs correction before parity can be assessed. |
| Velvet LEFTS 1/chart.ssc | parity_failure | 21184 | Automatic Lua GC changes allocation/table iteration order. The separately captured stopped-GC profile passes; it does not establish parity for automatic GC. |

## Supplemental profiles and controls

The `fixed60` profiles set the native `ConstantUpdateDeltaSeconds` preference to 1/60 second. This fixes the update delta; it does not impose a real-time 60 FPS frame cap. The long-frame roll control similarly uses a 0.2-second update delta.

Earlier invalid reduced controls and intermediate join-control failures remain in `extra-attempts.json`. The first feedback probes incorrectly used SetUpdateFunction on Def.Actor; the corrected ActorFrame probes are the valid controls below. Alternate profiles do not replace the primary case in the 503-case ledger.

| Case | Source | Latest result | Mismatches | Missing behavior or evidence |
| --- | --- | --- | ---: | --- |
| 3f7a546d6574982b-fixed60 | DS ULTIMATE LUA TEST/DS ULTIMATE LUA TEST.sm | native_lua_error | - | Inline-comma parsing is fixed in RSSP, and BackgroundEffect subscriber paths are fixed. Native now reports an overlay.lua tween overflow, including with a fixed 1/60-second update delta; this prevents accepting a complete clean oracle. |
| 82dbf1390bb50291-fixed60 | A Dramatic Irony/A Dramatic Irony.ssc | native_lua_error | - | Native reports Tween overflow: "&lt;type 20ScreenGameplayNormal&gt; ScreenGameplay/&lt;type 28ActorFrameAutoDeleteChildren&gt; Underlay/&lt;type 10BitmapText&gt; P1Score"; infinitely recursing ActorCommand?. A clean native run is required before accepting a fixture. |
| bank-versus-control | Bank Account/Bank Account.ssc | pass | 0 |  |
| beb47e811c5aafd3-fixed60 | james/james.sm | capture_observation_limit | - | Native reaches gameplay exit but the bounded trace loses observations: [{"dropped_events": 40761000}]. A streaming capture/replay path and a sufficient observation budget are needed; the truncated trace is rejected. |
| coverage-106fc438f82f1926 | Kita Saitama 2000/Kita Saitama 2000.ssc | pass | 0 |  |
| ee72a53d84d7fc88-fixed60 | james/james.ssc | capture_resource_limit | - | Native reaches gameplay exit but the bounded trace loses observations: [{"dropped_events": 40818375}]. A streaming capture/replay path and a sufficient observation budget are needed; the truncated trace is rejected. Capture postprocessing also ended as capture_resource_limit at 26G. |
| feedback-apollo-v2 | __pass2_controls/feedback-apollo-v2/control.sm | pass | 0 |  |
| feedback-megalovania-v2 | __pass2_controls/feedback-megalovania-v2/control.sm | pass | 0 |  |
| join-reload-v3 | __pass2_controls/join-reload/control.sm | pass | 0 |  |
| roll-long-frame | __pass2_controls/roll-long-frame/control.sm | pass | 0 |  |
| velvet-stopped-control | Velvet LEFTS 1/chart.ssc | pass | 0 |  |

See [all 503 cases](case-ledger.json), [full failure details](failure-details.json), [final replay results](final-replays.json), and [supplemental profiles](supplemental-results.json). Native candidates and full compressed comparison reports remain on their recorded VMs. Accepted fixtures are listed with verified compressed and decoded hashes in [published-archives.json](published-archives.json).
