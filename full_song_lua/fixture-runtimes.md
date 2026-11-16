# Song Lua fixture runtime guide

Updated **2026-11-16** from the stored November 15–16 Proxmox audit, repair-pass, and profiling logs. **No fixtures were rerun to create or refresh this guide.** Times below are rough planning measurements, not benchmark guarantees.

The November 15 inventory covers **503 primary simfiles** plus **11 supplemental profiles/controls**. Of the primary cases, **62** have repair-pass measurements (**P2**); **441** retain first-audit measurements (**P1**). November 16 updates are listed separately below. Different charts, profiles, archive versions, hardware, and build settings can change both cost and coverage.

Jump to [quick sets](#fast-regression-sets), [expensive fixtures](#expensive-passing-fixtures-to-schedule-deliberately), [known failures](#known-failures-run-when-working-on-the-named-gap), or [the complete lookup](#complete-passing-primary-lookup).

## At a glance

These are **replay-only** costs on the recorded Proxmox workers. Choose relevant coverage first, then use the timings to size the run.

| Testing need | Suggested selection | Recorded replay cost | Scheduling note |
| --- | --- | --- | --- |
| Small runtime regression checks | Four reduced controls below, plus pause and inactive-player join | About 35s total | Allow about a minute, plus setup; the old controls used a four-vCPU helper |
| Small real-song checks | My Penny, Get Into It SM, Apollo SM, both Sharkmode variants | About 2m 02s total | About 2m 37s together with all six controls; allow 4–6 minutes plus setup |
| Sharkmode-specific work | Either Sharkmode SSC, or both variants | About 29s each | Fresh capture alone adds about 3 minutes per variant |
| Join/reload or pause work | Relevant reduced control, then Anxiety SM/SSC or Megalovania | Controls 4–5s; songs 37–42s each | Use the November 16 passing results below |
| Hold/roll clock work | Roll-long-frame, Apollo SM, After Dark | About 4s, 31s, and 1m 22s | Add only the songs needed for the changed behavior |
| Large-trace work | Paint, fof, Mr Sandman, ArrowQuest | Roughly 6–18 minutes each | Recorded replay caps range from 42 to 84 GiB; schedule deliberately |
| A known unresolved failure | The matching diagnostic case/profile | Failed-attempt times only | A quick error is not a successful replay estimate |

The latest published primary ledger records **489 passes and 14 nonpasses**, combining historical and newer evidence. It is not a fresh pass of every chart. The complete lookup preserves the original November 15 timings; the updates immediately below supersede those entries where available.

<!-- pass3-runtimes:start -->
## November 16 updates

These completed runs add to the November 15 snapshot below. Use the [pass-three ledger](proxmox-pass3-2026-11-16/README.md) for current results; the older lookup and failure tables retain their original measurement context.

| Fixture | Successful replay | Native capture | Replay cap | Reference |
| --- | --- | --- | --- | --- |
| __pass3_controls/pause-v2/control.sm | 5s | 23s | 6G | Harness 0.1.99 capture; pause fix replay |
| __pass3_controls/join-inactive/control.sm | 4s | 20s | 6G | Harness 0.1.99 capture; pause fix replay |
| Anxiety/Anxiety.ssc | 42s | 3m 59s | 6G | Harness 0.1.99 capture; pause fix replay |
| Anxiety/Anxiety.sm | 41s | 3m 59s | 6G | Harness 0.1.99 capture; pause fix replay |
| After Dark/After Dark.ssc | 1m 22s | 5m 29s | 6G | Harness 0.1.99 capture; pause fix replay |
| Megalovania SM5 - [TaroNuke]/megalovania.sm | 37s | 3m 43s | 6G | Harness 0.1.99 capture; pause fix replay |
| [11] KENPO SAITO (DX) [Scrypts]/KENPO SAITO-chart.ssc | 10s | 2m 41s | 6G | Fresh harness 0.1.99; stopped-GC control only, primary still fails |
| 308-MISC-[lv.Quest] [Tech Spectrum Super - _TRUE GAMERS CLICK HERE - EXTRA CHARTS]/ArrowQuest.sm | 18m 08s | Retained capture | 84G | Retained native input |
| 308-MISC-[lv.Quest] [Tech Spectrum Super]/ArrowQuest.sm | 17m 50s | Retained capture | 84G | Retained native input |
| __pass3_controls/chart-selector/control.sm | 4s | 10s | 6G | Fresh harness 0.1.100; second Edit chart selected explicitly |
| __pass3_controls/chart-selector/control.ssc | 4s | 10s | 6G | Fresh harness 0.1.100; second Edit chart selected explicitly |
| __pass3_controls/styles/dance/control.ssc | 4s | 10s | 6G | Fresh harness 0.1.100; dance-single control |
| __pass3_controls/styles/dance/control.ssc | 4s | 10s | 6G | Fresh harness 0.1.100; dance-versus control |
| __pass3_controls/styles/dance/control.ssc | 4s | 11s | 6G | Fresh harness 0.1.100; dance-double control |
| __pass3_controls/styles/dance/control.ssc | 4s | 11s | 6G | Fresh harness 0.1.100; dance-couple control |
| __pass3_controls/styles/pump/control.ssc | 4s | 10s | 6G | Harness 0.1.100 capture; pump game/style fix replay; pump-single control |
| __pass3_controls/styles/pump/control.ssc | 4s | 10s | 6G | Harness 0.1.100 capture; pump game/style fix replay; pump-versus control |
| __pass3_controls/styles/pump/control.ssc | 4s | 10s | 6G | Harness 0.1.100 capture; pump game/style fix replay; pump-double control |
| __pass3_controls/styles/pump/control.ssc | 4s | 10s | 6G | Fresh harness 0.1.102; pump-couple control |

The latest **James SM failed capture** took **99m 55s** under a 148 GiB cap (harness 0.1.99). It was OOM-killed; retained native metadata also has dropped events and Lua errors. This is a failed-attempt cost, not a successful runtime estimate. Diagnostic preservation took additional time. See the [terminal evidence](proxmox-pass3-2026-11-16/james-terminal-retention.json).

These runners use release builds with debug information, frame pointers, LTO disabled and 16 codegen units. Most measurements used two-vCPU VMs; the 0.1.102 pump-couple control used the eight-vCPU native-build worker. This is a correctness-pass timing update, not a controlled performance comparison. Both ArrowQuest variants completed under an 84 GiB process cap; that cap is not a measured memory peak or a proven minimum.

Repeated heavy-fixture sampling is recorded separately in the [CPU profile report](proxmox-pass3-2026-11-16/profiles/README.md). Those times include profiler overhead and use the pre-fix baseline runner.
<!-- pass3-runtimes:end -->

<!-- routine-life-runtimes:start -->
## Routine-life timing update

The new [routine-life replays](proxmox-pass3-2026-11-16/routine-life-replays/README.md) add four passing, targeted controls. These are recorded release-runner replay costs on the eight-vCPU builder, before setup/decompression; no native captures were rerun for this update.

| Control | Replay | Replay cap | Accepted archive selector |
| --- | ---: | --- | --- |
| routine-life-dance | 3.6s | 6G | 074b7d148c9e5697 |
| routine-life-pump | 3.7s | 6G | 0542ab8faa6529d1 |
| style-dance-routine | 3.4s | 6G | 40789b891f44b2b6 |
| style-pump-routine | 3.5s | 6G | d7893e6a64776d03 |

Together these four controls took **14.2s** of serial replay. Use them for changes to routine shared life, history and Lua meter identity. At that baseline, the two manual routine controls failed on the team-statistics API. They now pass; use the newer routine-statistics timings below.

```powershell
cargo test --release --test full_song_lua -- --jobs 1 074b7d148c9e5697 0542ab8faa6529d1 40789b891f44b2b6 d7893e6a64776d03
```
<!-- routine-life-runtimes:end -->

<!-- routine-stats-runtimes:start -->
## Routine-statistics timing update

These measurements come from the completed correctness pass on the eight-vCPU builder, using an already-built release runner and uncompressed inputs. Updating this guide did not trigger captures or replays. All ten cases passed; fresh native capture for the two failure controls took about 16s and 15s respectively.

| Fixture | Replay | Replay cap | Accepted archive selector |
| --- | ---: | --- | --- |
| 280-MODS-[MASTER] Sharkmode/Sharkmode.ssc | 28.3s | 6G | 1a071285899f14c6 |
| Sharkmode [Ky_Dash]/Sharkmode.ssc | 28.7s | 6G | 81a02f3ebadfdd0e |
| __pass3_controls/routine-fail/dance/control.ssc | 3.3s | 6G | d09cd14d313b9cb6 |
| __pass3_controls/routine-fail/pump/control.ssc | 3.5s | 6G | 301452e340229cae |
| __pass3_controls/routine-life/dance/control.ssc | 3.5s | 6G | 074b7d148c9e5697 |
| __pass3_controls/routine-life/pump/control.ssc | 3.7s | 6G | 0542ab8faa6529d1 |
| __pass3_controls/routine-manual/dance/control.ssc | 3.6s | 6G | 7a09a08ad50bac6f |
| __pass3_controls/routine-manual/pump/control.ssc | 3.5s | 6G | c5821a08db402f2f |
| __pass3_controls/styles/dance/control.ssc | 3.6s | 6G | 40789b891f44b2b6 |
| __pass3_controls/styles/pump/control.ssc | 3.6s | 6G | d7893e6a64776d03 |

The eight routine controls total **28.2s** of serial replay. Use the four manual/failure controls for ordered team scoring, independent failure and statistics-query changes. Both Sharkmode regressions total **57.0s**. Allow additional time for builds, downloads and decompression.

```powershell
cargo test --release --test full_song_lua -- --jobs 1 d09cd14d313b9cb6 301452e340229cae 7a09a08ad50bac6f c5821a08db402f2f
```
<!-- routine-stats-runtimes:end -->

## Choosing what to run

1. For a DeadSync-only change, replay existing accepted archives first. Native recapture is needed when changing the harness, native engine, capture profile, or the behavior the existing trace observes.
2. Start with the reduced controls and small real-song set below. Add fixtures that exercise the changed behavior; a fast pass alone is not evidence of relevant coverage.
3. Reserve the large-memory fixtures for focused changes or a scheduled broader pass. Keep the known failures as targeted diagnostics rather than expecting a green smoke suite.
4. For a first scheduling allowance on comparable machines, budget about **1.5–2× the recorded replay time**, plus build/download/unpacking time. This is a planning margin, not a measured confidence interval.

## Fast regression sets

The four reduced controls total about **27s** of serial replay. The five small real-song fixtures add **2m 02s**. Combined: **2m 29s** measured replay, before setup overhead. All nine passed the final repair-pass runner.

| Fixture / profile | Replay | Fresh stages | Replay cap | Why include it | Archive selector |
| --- | --- | --- | --- | --- | --- |
| __pass2_controls/roll-long-frame/control.sm (roll-long-frame) | 4s | 23s | 12G | Roll decay under long update deltas | 1a253e2f7fcf8cdb |
| __pass2_controls/join-reload/control.sm (join-reload-v3) | 4s | 30s | 12G | P1-to-versus join/reload, player positions and style | 4660470145a7aca3 |
| __pass2_controls/feedback-apollo-v2/control.sm (feedback-apollo-v2) | 9s | 2m 58s | 12G | Reduced feedback-clock regression | ba83486aea0d7e36 |
| __pass2_controls/feedback-megalovania-v2/control.sm (feedback-megalovania-v2) | 10s | 3m 49s | 12G | Reduced feedback-clock regression; use the separate pause control for pause coverage | 91441f58d8d6e65b |
| My Penny/My Penny.ssc | 6s | 41s | 6G | Former native movie crash; recapture to test the video fix itself | b5d2abf91e4fbf74 |
| Get Into It/GetIntoIt.sm | 28s | 3m 01s | 6G | BackgroundEffect subscriber wrapper regression (SM) | eb0a426dfb314078 |
| Apollo/Apollo.sm | 31s | 3m 49s | 6G | Real-song feedback/roll timing (SM) | 902af9cf05568211 |
| 280-MODS-[MASTER] Sharkmode/Sharkmode.ssc | 29s | 3m 22s | 6G | Sharkmode MASTER regression | 1a071285899f14c6 |
| Sharkmode [Ky_Dash]/Sharkmode.ssc | 29s | 3m 23s | 6G | Sharkmode Ky_Dash regression | 81a02f3ebadfdd0e |

These selectors are unique prefixes of the exact accepted archive filenames, **not case IDs**. From the DeadSync root, after the selected fixture parts are available locally:

```powershell
cargo test --release --test full_song_lua -- --jobs 1 1a253e2f7fcf8cdb 4660470145a7aca3 ba83486aea0d7e36 91441f58d8d6e65b
cargo test --release --test full_song_lua -- --jobs 1 b5d2abf91e4fbf74 eb0a426dfb314078 902af9cf05568211 1a071285899f14c6 81a02f3ebadfdd0e
```

Two newer controls add about **9s** of serial replay. Both passed the pause-fix runner with zero implemented comparison mismatches or callback errors; see the [saved replay records](proxmox-pass3-2026-11-16/replays.json).

| Fixture / profile | Replay | Native capture | Replay cap | Why include it | Archive selector |
| --- | --- | --- | --- | --- | --- | --- |
| __pass3_controls/pause-v2/control.sm | 5s | 23s | 6G | Pause/Unpause commands and gameplay/audio integration | 98a73104dd109b454 |
| __pass3_controls/join-inactive/control.sm | 4s | 20s | 6G | Initially inactive P2 joining and reloading gameplay | dc0e3ee91d249468 |

```powershell
cargo test --release --test full_song_lua -- --jobs 1 98a73104dd109b454 dc0e3ee91d249468
```

The stored replay timers used already-built Linux runners and **uncompressed `.tar` inputs**. These commands use published `.tar.zst` fixtures, so compilation and decompression add time. A replay does not re-execute the native movie decoder; use a fresh native capture when testing a native video change.

## Reading the times and memory budgets

- **Replay** is the recorded DeadSync comparison stage, including its archive validation/report work. A time labelled “failed attempt” ends in failure and is not a completion estimate.
- **Capture** is the harness capture stage, including native gameplay and capture postprocessing. “Failed attempt” means the stage did not produce an accepted clean reference.
- **Fresh stages** sums capture + archive creation + the selected replay + packing for a pass. For a parity failure it stops after replay. When the final runner reused a capture, this is a sum across those recorded stages, not a separately measured end-to-end run. Missing stages stay unknown (—).
- The stage sum excludes VM provisioning, builds, queue waits, transfers, extra hashing/compression outside the named stages, and failed earlier retries. It is a lower planning baseline, not an elapsed fleet duration.
- **Replay cap** is the configured per-process cgroup memory limit in GiB (`6G` means 6 GiB), **not measured peak use or a proven minimum**. A small runtime with a large cap is still flagged for scheduling. The main workers had two vCPUs; the control helper had four. Concurrent workers shared the Proxmox host.
- Prefer serial execution for large-memory jobs unless total RAM headroom has been checked. Paint SM failed at 42 GiB and passed at 50 GiB. Both ArrowQuest replays failed at 50 GiB in the November 15 runs, then completed under an 84 GiB cap in the November 16 updates above.
- P1 timings are historical, including successful nested resource/dependency retries. P2 uses the final runner where available and its matching capture archive; superseded failures are not counted as fast successes.
- One selected chart/profile per simfile is timed. Historical zero-actor/zero-Lua-call and entrypoint guards still limit coverage; see the [coverage report](proxmox-audit-2026-11-15/coverage-summary.md). The four reduced controls and stopped-GC/versus profiles do not replace their primary song cases.

## Replay cost distribution

| Passing primary cases | P2 | P1 historical | Total |
| --- | --- | --- | --- |
| &lt;30 seconds | 20 | 335 | 355 |
| 30–60 seconds | 6 | 58 | 64 |
| 1–3 minutes | 7 | 44 | 51 |
| 3–10 minutes | 8 | 4 | 12 |
| 10 minutes or more | 1 | 0 | 1 |

These counts describe the November 15 snapshot and exclude its 20 nonpassing primary cases. The complete lookup below is grouped by successful replay cost and sorted fastest first; subsequent successful timings appear in the November 16 updates above.

## Expensive passing fixtures to schedule deliberately

| Song simfile | Replay | Capture | Fresh stages | Replay cap |
| --- | --- | --- | --- | --- |
| mr sandman/mr sandman.sm | 13m 52s | 4m 09s | 19m 23s | 42G |
| fof_guys/fof.ssc | 7m 35s | 11m 22s | 25m 19s | 50G |
| mawaru9/mawaru9.sm | 6m 34s | 6m 28s | 14m 12s | 26G |
| Paint the Town Red/PaintTheTownRed.ssc | 6m 20s | 8m 03s | 17m 40s | 50G |
| Paint the Town Red/PaintTheTownRed.sm | 6m 07s | 7m 56s | 17m 16s | 50G |
| What A Wonderful World/WAWW.sm | 5m 02s | 7m 53s | 16m 44s | 42G |
| mawaru7/mawaru7.sm | 4m 42s | 8m 08s | 15m 36s | 42G |
| Cloud99 (As Above Mix)/Song.ssc | 3m 54s | 7m 07s | 14m 05s | 26G |
| Cuphead [TaroNuke]/botanic.sm | 3m 41s | 6m 23s | 12m 30s | 42G |

## Known failures: run when working on the named gap

This table preserves the November 15 failed-attempt timings and diagnoses. Anxiety SM/SSC, After Dark, Megalovania and both ArrowQuest variants subsequently passed; use their November 16 timings above and the [pass-three ledger](proxmox-pass3-2026-11-16/README.md) for the latest published status. Megalovania's fresh pass does not establish the cause of its earlier mismatches. The separate pause control reproduced a runtime gap that has since been fixed and now passes. The remaining failures are diagnostic targets, not part of the passing quick sets. A native script error, timeout, truncated capture, or OOM can finish quickly without providing useful parity coverage.

| Song simfile | Capture | Replay | Capture / replay cap | November 15 result / reason | Case ID |
| --- | --- | --- | --- | --- | --- |
| [11] KENPO SAITO (DX) [Scrypts]/KENPO SAITO-chart.ssc | 2m 41s | 10s | 6G / 6G | parity_failure: 7 same-frame traversal-order mismatches. | a170dd312f720cd4 |
| After Dark/After Dark.ssc | 5m 25s | 1m 12s | 6G / 6G | parity_failure: 175 remaining hold-tail/feedback timing mismatches. | fbe89f6bae9565a6 |
| Megalovania SM5 - [TaroNuke]/megalovania.sm | 3m 45s | 30s | 6G / 6G | parity_failure: 6 pause/gameplay-clock mismatches. | c3e0c410f04c30dd |
| Velvet LEFTS 1/chart.ssc | 2m 25s | 26s | 6G / 42G | parity_failure: 21,184 automatic-GC/table-order mismatches; stopped-GC is a separate profile. | 8f4d4741245868cf |
| 242-MISC.[lv.02] ChikuTaku/ChikuTaku.ssc | 4m 03s (failed attempt) | — | 6G / — | native_lua_error: Authored native movie setup passes a nil musicrate to Sprite.rate. Supply/resolve the song dependency before accepting a native oracle. | d007bb219d9d393a |
| 308-MISC-[lv.Quest] [Tech Spectrum Super - _TRUE GAMERS CLICK HERE - EXTRA CHARTS]/ArrowQuest.sm | 3m 21s (recovery only) | 22m 58s (failed attempt) | 50G / 50G | replay_resource_limit: No complete comparison under the recorded resource/observation limits. Streaming trace parsing/replay or a larger isolated budget is still needed; do not infer a semantic verdict. | 67053c6979c0becb |
| 308-MISC-[lv.Quest] [Tech Spectrum Super]/ArrowQuest.sm | 46m 04s | 23m 48s (failed attempt) | 50G / 50G | replay_resource_limit: No complete comparison under the recorded resource/observation limits. Streaming trace parsing/replay or a larger isolated budget is still needed; do not infer a semantic verdict. | 85aa930d114b2262 |
| [FULL SONG] ChikuTaku [wrsw]/ChikuTaku.ssc | 4m 03s (failed attempt) | — | 6G / — | native_lua_error: Authored native movie setup passes a nil musicrate to Sprite.rate. Supply/resolve the song dependency before accepting a native oracle. | 2bb9c0a9995617ac |
| A Dramatic Irony/A Dramatic Irony.ssc | 20m 08s (failed attempt) | — | 26G / — | native_lua_error: Native reports Tween overflow: "&lt;type 20ScreenGameplayNormal&gt; ScreenGameplay/&lt;type 28ActorFrameAutoDeleteChildren&gt; Underlay/&lt;type 10BitmapText&gt; P1Score"; infinitely recursing ActorCommand?. A clean native run is required before accepting a fixture. | 82dbf1390bb50291 |
| Anxiety/Anxiety.sm | 3m 57s (failed attempt) | — | 6G / — | native_lua_error: The P1-to-versus join/reload control now passes, including roster, style, and positions. This authored native run fails in Simply Love TrackFailTime.lua:121 after P2 joins without autoplay/stream metrics. A clean native reference and a complete inactive-player profile are still needed. Unjoin and physical-P2-origin joins are not established. | 7c462fc586e600b3 |
| Anxiety/Anxiety.ssc | 3m 57s (failed attempt) | — | 6G / — | native_lua_error: The P1-to-versus join/reload control now passes, including roster, style, and positions. This authored native run fails in Simply Love TrackFailTime.lua:121 after P2 joins without autoplay/stream metrics. A clean native reference and a complete inactive-player profile are still needed. Unjoin and physical-P2-origin joins are not established. | 3effbc28e93b70bc |
| Bank Account/Bank Account.ssc | 1m 38s (failed attempt) | — | 6G / — | native_lua_error: The single-player profile accesses an absent PlayerP2. A separate versus capture passes; it does not replace this primary profile. | 001abcd0e01187de |
| Cursed Metamorph - [Zaia]/saved/Cursed Metamorph.ssc | 2s (failed attempt) | — | 6G / — | native_capture_error: The saved chart is missing its music dependency; the native capture never yields a valid completed reference. | cf1c3df5d6e9f28b |
| DS ULTIMATE LUA TEST/DS ULTIMATE LUA TEST.sm | 12m 54s (failed attempt) | — | 6G / — | native_lua_error: Inline-comma parsing is fixed in RSSP, and BackgroundEffect subscriber paths are fixed. Native now reports an overlay.lua tween overflow, including with a fixed 1/60-second update delta; this prevents accepting a complete clean oracle. | 3f7a546d6574982b |
| Happiness/Happiness.ssc | 3m 33s (failed attempt) | — | 6G / — | native_lua_error: Native diva.lua:1092 reads an exhausted break-length table after foreground restart. Resolve the authored lifecycle error before accepting a native oracle. | 715ba44e314f2f6e |
| Haxo (Sharks Remix) [sorae]/haxo.ssc | 2m 03s (failed attempt) | — | 6G / — | native_lua_error: Authored native effectmagnitude call has too few numeric arguments; the song needs a valid native execution before comparison. | 00b8031e64c3cf41 |
| james/james.sm | 20m 30s (failed attempt) | — | 26G / — | capture_observation_limit: Native reaches gameplay exit but the bounded trace loses observations: [{"dropped_events": 41824750}]. A streaming capture/replay path and a sufficient observation budget are needed; the truncated trace is rejected. | beb47e811c5aafd3 |
| james/james.ssc | 20m 28s (failed attempt) | — | 26G / — | capture_observation_limit: Native reaches gameplay exit but the bounded trace loses observations: [{"dropped_events": 41801125}]. A streaming capture/replay path and a sufficient observation budget are needed; the truncated trace is rejected. | ee72a53d84d7fc88 |
| Lesson by DJ/Lesson by DJ.sm | 2s (failed attempt) | — | 6G / — | no_selectable_chart: The source SM has no selectable chart (malformed NOTES header). Repair the corpus simfile before a full native run. | c5080f1c121d14e5 |
| Sequential Dreambox - [Zaia]/Sequential Dreambox.ssc | 5m 39s (failed attempt) | — | 6G / — | native_lua_error: New native script-error observation exposes FastEnd.lua:47: '&lt;eof&gt;' expected near 'local'. The original zero-Lua-call pass was invalid; the authored script needs correction before parity can be assessed. | c893672a26e2b70c |

The EXTRA CHARTS ArrowQuest capture timing is **recovery/postprocessing only** after a host OOM; its original native gameplay time is not included. The failed ArrowQuest replay durations above are superseded for planning by the successful 17–18 minute replays in the November 16 updates. James loses roughly 42 million events at the normal cap; repeating unchanged settings is not a parity test.

## Supplemental profiles and controls

Profile IDs matter: Bank Account versus and Velvet stopped-GC pass while their primary profiles remain nonpassing. `fixed60` fixes the update delta to 1/60 second; it does not impose a real-time FPS cap.

| Profile ID / song | Capture | Replay | Fresh stages | Replay cap | Result |
| --- | --- | --- | --- | --- | --- |
| 3f7a546d6574982b-fixed60 — DS ULTIMATE LUA TEST/DS ULTIMATE LUA TEST.sm | 12m 55s (failed attempt) | — | — | — | native_lua_error |
| 82dbf1390bb50291-fixed60 — A Dramatic Irony/A Dramatic Irony.ssc | 23m 44s (failed attempt) | — | — | — | native_lua_error |
| bank-versus-control — Bank Account/Bank Account.ssc | 1m 40s | 14s | 2m 05s | 26G | pass |
| beb47e811c5aafd3-fixed60 — james/james.sm | 26m 43s (failed attempt) | — | — | — | capture_observation_limit |
| coverage-106fc438f82f1926 — Kita Saitama 2000/Kita Saitama 2000.ssc | 3m 42s | 1m 37s | 6m 36s | 26G | pass |
| ee72a53d84d7fc88-fixed60 — james/james.ssc | 24m 25s (failed attempt) | — | — | — | capture_resource_limit |
| feedback-apollo-v2 — __pass2_controls/feedback-apollo-v2/control.sm | 2m 42s | 9s | 2m 58s | 12G | pass |
| feedback-megalovania-v2 — __pass2_controls/feedback-megalovania-v2/control.sm | 3m 33s | 10s | 3m 49s | 12G | pass |
| join-reload-v3 — __pass2_controls/join-reload/control.sm | 20s | 4s | 30s | 12G | pass |
| roll-long-frame — __pass2_controls/roll-long-frame/control.sm | 13s | 4s | 23s | 12G | pass |
| velvet-stopped-control — Velvet LEFTS 1/chart.ssc | 2m 23s | 25s | 3m 03s | 6G | pass |

## Complete passing primary lookup

**P2** = repair-pass timing; **P1** = historical first-audit timing. All rows in this section are recorded passes. For exact chart/style/profile, look up the **case ID** in the source JSON linked below. The 483 rows here plus the 20 failure rows above cover all 503 primary cases.

### <30 seconds

| Song simfile | Replay | Capture | Fresh stages | Replay cap | Timing | Case ID |
| --- | --- | --- | --- | --- | --- | --- |
| GREAT GREAT/GREAT GREAT.ssc | 4s | 13s | 25s | 6G | P1 | 56e9155700aed9db |
| copter/copter.sm | 4s | 19s | 31s | 6G | P1 | c78adffccf3e4654 |
| Midnight Madness/midnight.sm | 4s | 34s | 46s | 6G | P1 | 78332255bc11a219 |
| Hallways/hallways.ssc | 4s | 30s | 42s | 6G | P1 | 0932e452fa2d3075 |
| copter/copter.ssc | 4s | 19s | 32s | 6G | P1 | 104b5f9491922f7e |
| Gaming in 2018/Gaming in 2018.ssc | 5s | 33s | 44s | 6G | P1 | d63450ca44af90f7 |
| freg/freg.sm | 5s | 31s | 43s | 6G | P1 | 9332334d6a9e3f7a |
| My Penny/My Penny.ssc | 6s | 28s | 41s | 6G | P2 | 939315314b14098a |
| Kuru Kuru kururin/Kuru Kuru kururin.ssc | 6s | 41s | 54s | 6G | P1 | 51f73c5bb27172dd |
| U.N. Owen Was Who [Hyperhero2]/unowenwaswho.sm | 6s | 1m 22s | 1m 35s | 6G | P1 | eee0125bc9fcae89 |
| U.N. Owen Was Who [Hyperhero2]/unowenwaswho.ssc | 6s | 1m 21s | 1m 35s | 6G | P1 | 81e5965dfe717a01 |
| Macarena/Macarena.ssc | 6s | 1m 36s | 1m 50s | 6G | P1 | f44a62dd9459fee2 |
| c'est business/c'est business.ssc | 6s | 31s | 47s | 6G | P1 | ec496ff39821cc5c |
| Waiting/Waiting.ssc | 7s | 1m 37s | 1m 51s | 6G | P1 | 07ac78a6da76a5b5 |
| Bank Account/Bank Account.sm | 7s | 1m 36s | 1m 50s | 6G | P1 | 8e2cc50f6bd76919 |
| Ztar Trek/steps.sm | 7s | 1m 48s | 2m 03s | 6G | P1 | 5be5d671acef02e8 |
| MAX 300 (BlaZe MIX) - [Aoreo]/wargame.ssc | 7s | 1m 34s | 1m 49s | 6G | P1 | c5be063e4f92e240 |
| I Like To Move It/I Like To Move It.ssc | 7s | 1m 47s | 2m 02s | 6G | P1 | 4c89aef6cbd8e6a8 |
| Wobbpotato [Blue Shift Phase 1]/wobbpotato.ssc | 7s | 1m 50s | 2m 04s | 6G | P1 | 060dd2e43146562d |
| Fiji (Lange Remix)/Fiji (Lange Remix).ssc | 7s | 1m 45s | 1m 59s | 6G | P1 | 3939de0493c8ea15 |
| Retrospective/Retrospective.ssc | 7s | 2m 59s | 3m 14s | 6G | P1 | 84fccbe6e63d458a |
| Wobbpotato [Egg Carton 3]/wobbpotato.ssc | 7s | 1m 50s | 2m 05s | 6G | P1 | f7a2bad131d8842f |
| Backwards/Backwards.sm | 7s | 1m 58s | 2m 14s | 6G | P1 | ae1dd79e71a05e9f |
| jeans/abj.sm | 7s | 45s | 1m 00s | 6G | P1 | 244d988e5da3a481 |
| I Really Like You [dbk2]/I Really Like You.sm | 7s | 2m 07s | 2m 22s | 6G | P1 | 18ce02683c733e00 |
| If You Crump Stand Up/crump.sm | 8s | 2m 14s | 2m 29s | 6G | P1 | a760ce2ddf9433d4 |
| [12] Ascendanz/Ascendanz.ssc | 8s | 2m 06s | 2m 23s | 6G | P1 | 9e5cb2c801c247a3 |
| Kita Saitama 2000/Kita Saitama 2000.ssc | 8s | 2m 07s | 2m 22s | 6G | P1 | 106fc438f82f1926 |
| OK/OK.ssc | 8s | 2m 00s | 2m 16s | 6G | P1 | 9bb480a1fda3b13d |
| Max 300/MAX 300.ssc | 8s | 1m 39s | 1m 54s | 6G | P2 | b8627b23d498bfe5 |
| Number 9/1556 - Number 9.sm | 8s | 2m 08s | 2m 24s | 6G | P1 | 78f10d924a8b9bd9 |
| Ascendanz/Ascendanz.ssc | 8s | 2m 06s | 2m 21s | 6G | P1 | 11205e6997187207 |
| Magic Torus/torus3.sm | 8s | 1m 18s | 1m 34s | 6G | P1 | d1e60f5644971194 |
| Loyal Divide [TaroNuke]/Loyal Divide.sm | 8s | 2m 23s | 2m 39s | 6G | P1 | 12e625ce625e261a |
| A Op.01/A Op.01.ssc | 8s | 2m 07s | 2m 22s | 6G | P1 | e7211a0eeab973b5 |
| Pop/Pop.ssc | 8s | 2m 05s | 2m 20s | 6G | P1 | 1dd3b7631ceef5fc |
| Lots of Spices - [tari]/spices.ssc | 8s | 2m 09s | 2m 26s | 6G | P1 | 8bbbbd0a227889ec |
| Rainbow Road [chairodactyl] - Cameron Wiggers/Rainbow Road.ssc | 8s | 1m 46s | 2m 02s | 6G | P1 | 3ea797a87e1c8d3d |
| You are Goomba Play ITG/You are Gooma Play ITG.ssc | 8s | 1m 23s | 1m 40s | 6G | P1 | 68da023865debbc2 |
| Crab Nicholson Extreme Sleepover/Crab Nicholson Extreme Sleepover.sm | 8s | 1m 54s | 2m 09s | 6G | P1 | 9e59effe9cf00022 |
| Distraction/sm.sm | 8s | 2m 03s | 2m 19s | 6G | P1 | 296b336535204262 |
| the fresh prince of bel air (razihel remix)/steps.sm | 8s | 2m 21s | 2m 37s | 6G | P1 | 38602f3b4c159b26 |
| Potion [Flood_]/Shisui Michiru - Potion (Cut Ver).sm | 8s | 2m 26s | 2m 44s | 6G | P1 | 5996cb1bf517a580 |
| Genshin Quiz/Megaquiz.ssc | 8s | 2m 00s | 2m 16s | 6G | P1 | 880341a8f13b03d2 |
| Vector Field/Vector Field.ssc | 8s | 2m 10s | 2m 27s | 6G | P1 | f491b527eed47496 |
| Rayc Fire 2/Rayc Fire 2.ssc | 8s | 2m 30s | 2m 46s | 6G | P1 | 53da0d7a82127af7 |
| You are Goomba Play ITG/You are Gooma Play ITG.sm | 8s | 1m 24s | 1m 41s | 6G | P1 | 5d994d7d27006aa2 |
| Oil Ocean Act 2/steps.sm | 8s | 2m 43s | 2m 59s | 6G | P1 | 9ceaae2441fe1203 |
| Ultra B+K/ultrabk.ssc | 8s | 2m 10s | 2m 26s | 6G | P1 | 1a729c17bff33266 |
| Boys/Boys.ssc | 8s | 2m 02s | 2m 18s | 6G | P1 | 40c7a991f83115c4 |
| MODULO/modulo.ssc | 8s | 2m 08s | 2m 27s | 6G | P1 | de0ce4430a303dfb |
| Rayc Fire 2/Rayc Fire 2.sm | 8s | 2m 30s | 2m 46s | 6G | P1 | 5a998294ae8b6156 |
| gone_KidFresino/song.ssc | 8s | 2m 24s | 2m 41s | 6G | P1 | 14f0c3e28694fb27 |
| minefield surfing_1/minefield.ssc | 8s | 2m 07s | 2m 24s | 6G | P1 | 6defe5eb3ebc85fe |
| BBKKBKK [UPS5 SM5]/BBKKBKK.ssc | 9s | 2m 16s | 2m 32s | 6G | P1 | e2baf9034767a8e9 |
| ShockWAVE Syndrome  [-YOSEFU-]/ShockWAVE Syndrome.ssc | 9s | 2m 18s | 2m 34s | 6G | P1 | 98bb8765cc53dc69 |
| wah-propaganwah (habstrakt remix) (ddrillini remix)/Propaganda (Habstrakt Remix).ssc | 9s | 2m 36s | 2m 52s | 6G | P1 | 39e764adfd847c25 |
| Gossipo Perpetuo [chairodactyl] - Cameron Wiggers/gossiperpet.ssc | 9s | 2m 12s | 2m 30s | 6G | P1 | 6f6d5a8f41c6ce73 |
| Shine!/Shine!.ssc | 9s | 2m 24s | 2m 41s | 6G | P1 | c4d41aebaead65d8 |
| crew -All Hands on the Deck-/crew.ssc | 9s | 2m 30s | 2m 48s | 6G | P1 | bf0cfd32a9223792 |
| Subway Surfers/subwaysurfers.ssc | 9s | 2m 26s | 2m 42s | 6G | P1 | c5c6f1c59893383a |
| Stepping Music/simfile.ssc | 9s | 2m 46s | 3m 03s | 6G | P1 | 921efbca081f6940 |
| Tower Power Pokey  Battle/Tower Power Pokey Battle.ssc | 9s | 2m 34s | 2m 51s | 6G | P1 | 27bf34c598723a33 |
| BBKKBKK [UPS 3]/BBKKBKK.ssc | 9s | 2m 16s | 2m 32s | 6G | P1 | 6b8413132f27f5ca |
| mawaru1/mawaru.sm | 9s | 2m 35s | 2m 52s | 6G | P1 | 206471d331202435 |
| Do the Mario/DoTheMario.ssc | 9s | 56s | 1m 17s | 6G | P1 | adb2c65e9f109a2a |
| new earth/new earth.ssc | 9s | 2m 08s | 2m 25s | 6G | P1 | df3e735bcf803da2 |
| K-Pop Foxture/K-Pop Foxture.ssc | 9s | 2m 40s | 2m 57s | 6G | P1 | fea1233a68245931 |
| Kizuato - [Zaia]/Kizuato.ssc | 9s | 2m 28s | 2m 46s | 6G | P1 | 620418b6946c40ee |
| In the Hall of the Mountain King [dbk2]/In the Hall of the Mountain King.ssc | 9s | 1m 36s | 1m 53s | 6G | P1 | 52e5b78957c3a903 |
| BBKKBKK [UPS 4]/BBKKBKK.ssc | 9s | 2m 16s | 2m 33s | 6G | P2 | 4295240e49b7f6c2 |
| flowers/flowers.ssc | 9s | 1m 35s | 1m 52s | 6G | P1 | 32834d1a966ea8be |
| Jokes/Write Final Round.ssc | 9s | 2m 07s | 2m 24s | 6G | P1 | 8d53a4cc0927959a |
| spooky (SM 12)/spooky (Tech-Stam cut).ssc | 9s | 2m 20s | 2m 37s | 6G | P1 | b9d56e264b9e6a25 |
| flowers [R.I.G.H.T.S]/flowers.ssc | 9s | 1m 35s | 1m 53s | 6G | P1 | d03669153c4863d3 |
| cards/sm.ssc | 9s | 3m 30s | 3m 48s | 6G | P1 | 05f550917c3e16a7 |
| edamame (except bbno$ produced it under C&amp;A)/edamame.sm | 9s | 2m 37s | 2m 55s | 6G | P1 | a8dda3ade2a6e0ee |
| Brain Implosion Energy Drink/Brain Implosion Energy Drink.ssc | 10s | 2m 22s | 2m 41s | 6G | P1 | 7a09b36f8f97e343 |
| Electrified/Electrified cut.ssc | 10s | 2m 44s | 3m 02s | 6G | P1 | 97f365feb5decf55 |
| Watermelon/Watermelon.ssc | 10s | 1m 44s | 2m 04s | 6G | P1 | 02d346474091aa01 |
| Aegleseeker/Aegleseeker.ssc | 10s | 2m 34s | 2m 51s | 6G | P1 | 62164b08489d3045 |
| Stay Alive/Stay Alive.ssc | 10s | 2m 39s | 2m 57s | 6G | P1 | 3dec5442144ad3de |
| Daywalker/Daywalker.ssc | 10s | 2m 26s | 2m 44s | 6G | P1 | 23a6e9d21e021dc7 |
| Tacos/Tacos.ssc | 10s | 2m 23s | 2m 42s | 6G | P1 | df0ec2c374700550 |
| 1035/1035.sm | 10s | 2m 58s | 3m 15s | 6G | P1 | 38e7b13ff8349ea0 |
| Cat Hack/Cat Hacks.sm | 10s | 3m 13s | 3m 30s | 6G | P1 | 3793287dc1cc7dd5 |
| Among Us In Real Life - Single/Official Among Us In Real Life Official Simulation File - Rebecca Zamolo Shorts.ssc | 10s | 2m 45s | 3m 04s | 6G | P1 | b34d885934f9816a |
| Numujika ac.10/Numujika ac.10.sm | 10s | 2m 18s | 2m 36s | 6G | P1 | 109c519c4b0077dc |
| [recognize m.] happy century/steps.ssc | 10s | 2m 28s | 2m 46s | 6G | P1 | f3398d715019375f |
| Wake Up/Wake Up.ssc | 10s | 2m 18s | 2m 37s | 6G | P1 | 237dd9b096c32365 |
| cards/sm.sm | 10s | 3m 31s | 3m 49s | 6G | P1 | 5e06cad06be50156 |
| edamame (except bbno$ produced it under C&amp;A)/edamame.ssc | 10s | 2m 38s | 2m 58s | 6G | P1 | 77cb8aa401454c51 |
| No.13/no13.ssc | 10s | 3m 04s | 3m 24s | 6G | P1 | 4a4d71253d9852e3 |
| TRIP MACHINE -Resuscitation MIX-/TRIP MACHINE -Resuscitation MIX-.ssc | 10s | 2m 06s | 2m 25s | 6G | P1 | 073248942b05d007 |
| Doubles-45-HALF-[MASTER] Tacos/Tacos.ssc | 10s | 2m 24s | 2m 44s | 6G | P1 | a8dc80dd27222e5c |
| redesign your logo/Redesign your logo.ssc | 10s | 2m 48s | 3m 06s | 6G | P1 | 70a1b24b95011c56 |
| Up Up Up Up/Up Up Up Up.sm | 10s | 3m 27s | 3m 45s | 6G | P1 | 806bae8c0e4bf292 |
| STAGE 0.ac11/STAGE 0.ac11.sm | 10s | 2m 25s | 2m 44s | 6G | P1 | 325fe5cb2095040a |
| Dig Dug Theme/Dig Dug Theme.ssc | 10s | 2m 55s | 3m 14s | 6G | P1 | a1bd31803af79b4f |
| Abraham's OP/Abraham's OP.ssc | 10s | 3m 10s | 3m 29s | 6G | P1 | 3bf6315645e3f729 |
| MISSION SPUTNIK/sputnik.ssc | 10s | 3m 00s | 3m 19s | 6G | P1 | 2f042faf38f4b9f9 |
| [12] Tacos [DX]/Tacos.ssc | 10s | 2m 23s | 2m 42s | 6G | P1 | a2f07851a4cfe0ed |
| Cat Hack/Cat Hacks.ssc | 10s | 3m 13s | 3m 31s | 6G | P1 | 273170f92248917b |
| It's Showtime/mettaton.ssc | 10s | 2m 04s | 2m 23s | 6G | P1 | 789f5179ede5b073 |
| We're Finally Landing/landing.ssc | 10s | 2m 06s | 2m 26s | 6G | P1 | 53b886f9a09f3dbc |
| Cursed 2/Cursed 2.sm | 10s | 2m 03s | 2m 25s | 6G | P1 | 3f521ea2b97717f2 |
| Cyberpunk 2077/Cyberpunk 2077.ssc | 10s | 3m 02s | 3m 21s | 6G | P2 | 5a130a6b5626f565 |
| Just a Friend To  You/Just a Friend To  You.sm | 10s | 2m 47s | 3m 06s | 6G | P1 | 460ff73ccd45513d |
| Just a Friend To  You/Just a Friend To  You.ssc | 10s | 2m 47s | 3m 06s | 6G | P1 | 65fa29b0969393f2 |
| INAZUMA (Gio)/INAZUMA.ssc | 10s | 2m 26s | 2m 45s | 6G | P2 | 131298138770f9dd |
| Choices - [Aoreo]/Choices.ssc | 11s | 3m 21s | 3m 41s | 6G | P1 | 21f9b53056dc9e93 |
| itg bloodrush 2005/itg bloodrush 2005.sm | 11s | 1m 54s | 2m 16s | 6G | P1 | 4b519e5e0919eeab |
| Ultra B.B.K.K.B.K.K/Ultra B.B.K.K.B.K.K.sm | 11s | 2m 11s | 2m 32s | 6G | P1 | 8e96ced0ed049452 |
| Ultra B.B.K.K.B.K.K/Ultra B.B.K.K.B.K.K.ssc | 11s | 2m 11s | 2m 33s | 6G | P1 | 4d47cb45c917c401 |
| Cursed 2/Cursed 2.ssc | 11s | 2m 02s | 2m 24s | 6G | P1 | df36e5247122645f |
| spooky (SX 14)/spooky (Tech-Stam cut).ssc | 11s | 3m 15s | 3m 34s | 6G | P1 | 5116534ebb388ef9 |
| flores sulphuris - [Zaia]/flores sulphuris.ssc | 11s | 3m 05s | 3m 25s | 6G | P1 | 07b39a43c148956f |
| Maware! Setsugetsuka (ric3show3r bootleg)/maware ric3show3r.ssc | 11s | 1m 50s | 2m 12s | 6G | P1 | 8132e675d480f24a |
| Hello Gordon [chairodactyl] - Cameron Wiggers/Hello Gordon.ssc | 11s | 3m 11s | 3m 32s | 6G | P1 | 646d92bf866e3520 |
| assgore/goatdad.sm | 11s | 3m 19s | 3m 43s | 6G | P1 | 9a17ba96ce6150bd |
| Reach The Light Switch, Without Asking you/Reach The Light Switch, Without Asking you.ssc | 11s | 1m 53s | 2m 12s | 6G | P1 | d7e5f13cbd826448 |
| Life Cheating Game/lifecheatinggame.ssc | 11s | 2m 31s | 2m 51s | 6G | P1 | f5b4e9da4859815f |
| Impulse/impulse.ssc | 12s | 3m 23s | 3m 44s | 6G | P1 | 3b081186c1ca2328 |
| Neon Nights - [Zaia]/Neon Nights.ssc | 12s | 1m 21s | 1m 44s | 6G | P1 | e5e5893913545b91 |
| No Role Modelz/No Role Modelz.sm | 12s | 4m 23s | 4m 42s | 6G | P1 | bd08439da170a94d |
| Impulse/impulse.sm | 12s | 3m 24s | 3m 44s | 6G | P1 | 97e8f5f120b2f55d |
| rite of spring/rite.ssc | 12s | 2m 40s | 3m 01s | 6G | P1 | ecddbf8409d180ed |
| Airman First Class - [glory limited.]/kpopmix.ssc | 12s | 3m 37s | 3m 58s | 6G | P1 | 9f4e88c5d17b7f5f |
| Hispanic Panic/sm.sm | 12s | 3m 23s | 3m 43s | 6G | P1 | 5e07d020b22593a3 |
| Bodies/Bodies.ssc | 12s | 2m 15s | 2m 38s | 6G | P1 | d9cd7f024926e6c6 |
| Lower Times/Lower Times.ssc | 12s | 3m 40s | 4m 00s | 6G | P1 | ea1b769546ad69b6 |
| Vtubers Never Die! [Gpop]/Vtubers Never Die!.ssc | 12s | 2m 22s | 2m 48s | 6G | P1 | 6a8fe1f9addfcd9d |
| Other Guy/Other Guy.ssc | 12s | 2m 40s | 3m 03s | 6G | P1 | aa3cfa1ee20e932a |
| Lesson by DJ/Lesson by DJ.ssc | 12s | 1m 47s | 2m 09s | 6G | P1 | d3b292637800da81 |
| Pale/Pale.ssc | 13s | 2m 44s | 3m 07s | 6G | P1 | c4c9ebb00ddbcb9b |
| mawaru2/mawaru2.sm | 13s | 2m 57s | 3m 20s | 6G | P1 | 0f004f6b16b1af5d |
| Fortuna Redux - [Zaia]/Fortuna Redux.sm | 13s | 4m 19s | 4m 41s | 6G | P1 | 3bd84fe8e4f26966 |
| no touchy/no touchy.ssc | 13s | 2m 08s | 2m 34s | 6G | P1 | ec101fa538c68537 |
| [12] Blacksphere (SX) [Exschwasion]/music.ssc | 13s | 2m 13s | 2m 38s | 6G | P1 | 3990bedfecf8631f |
| I Really Like You [dbk2]/I Really Like You.ssc | 13s | 3m 57s | 4m 19s | 6G | P1 | 9e521f84bff0597a |
| My Exes Bestfriend/ExBestFriend.sm | 13s | 2m 31s | 2m 57s | 6G | P1 | 0c434e5ce8baba92 |
| Blacksphere/music.ssc | 13s | 2m 13s | 2m 39s | 6G | P1 | 249a5bb1989d2833 |
| Pale/Pale.sm | 13s | 2m 44s | 3m 10s | 6G | P1 | 1c710206f5bc78dd |
| SharpNel/HashtagNel.ssc | 13s | 3m 19s | 3m 42s | 6G | P1 | ef844878f91db8aa |
| Bad Apple!!/Bad Apple!!.sm | 13s | 3m 39s | 4m 03s | 6G | P2 | 94e45bc78c33fb2c |
| Dimmadome/doug dimmadome owner of the dimmsdale dimmadome.sm | 13s | 1m 46s | 2m 12s | 6G | P1 | 5015fabc389a99af |
| Stella Glow/Stella Glow.ssc | 14s | 2m 08s | 2m 30s | 6G | P1 | 5ca8e4c5c01e98d2 |
| Vanishing Point - [Zaia][FX]/Vanishing Point.sm | 14s | 5m 01s | 5m 24s | 6G | P1 | ce08596ced8c1a82 |
| Over the Top - [Zaia][FX]/Over the Top.sm | 14s | 4m 28s | 4m 50s | 6G | P1 | f996111c68150ced |
| Longinus - [Zaia]/Longinus.sm | 14s | 4m 48s | 5m 11s | 6G | P1 | c470f90cddf5720c |
| 307-MISC-[lv.Death] [Tech Spectrum Super - _TRUE GAMERS CLICK HERE - EXTRA CHARTS]/The Boys Are Back in Town (to kill you).ssc | 14s | 1m 31s | 1m 58s | 6G | P1 | 591fcd1751af2aef |
| Jumper/Jumper.sm | 14s | 3m 33s | 3m 54s | 6G | P1 | 6a232e8676f57129 |
| 307-MISC-[lv.Death] [Tech Spectrum Super]/The Boys Are Back in Town (to kill you).ssc | 14s | 1m 31s | 1m 58s | 6G | P1 | 5d22cf5bb4768892 |
| ghost [Telperion]/ghost.ssc | 14s | 2m 24s | 2m 50s | 6G | P1 | 5dc99ec275466e11 |
| Marshall Maximizer/marshall maximizer.ssc | 14s | 2m 27s | 2m 55s | 6G | P1 | a2bae3060fde69c0 |
| 188-HS-Holdswitch[lv.08] the shadow/theshadow.ssc | 14s | 2m 20s | 2m 47s | 6G | P1 | 37b26bf6ff08a1e9 |
| 271-MODS-[lv.01] Spooky/1.09 - Spooky.ssc | 14s | 2m 10s | 2m 35s | 6G | P1 | c6d5fc7e87738009 |
| My Exes Bestfriend/ExBestFriend.ssc | 15s | 2m 31s | 2m 59s | 6G | P1 | d6d3774fd5f3b1d4 |
| Accelerator/Accelerator.sm | 15s | 1m 55s | 2m 23s | 6G | P1 | 1c1edbef2eb28d0b |
| The Boys Are Back in Town (to kill you)/The Boys Are Back in Town (to kill you).ssc | 15s | 1m 31s | 1m 58s | 6G | P1 | d9e2bf87d1bcaf89 |
| Paradise [Cringle Desolation]/Paradise.sm | 15s | 2m 57s | 3m 24s | 6G | P1 | f1feeb3c5ba4ce9f |
| Accelerator/Accelerator.ssc | 15s | 1m 55s | 2m 23s | 6G | P1 | 52fba3adab035b32 |
| ICON KILLER - [Zaia + StarrySergal + dimo + Brother Mojo]/ICON KILLER.ssc | 15s | 1m 54s | 2m 22s | 6G | P1 | a479b8d3ca42be7b |
| Paradise/Paradise.sm | 15s | 2m 57s | 3m 24s | 6G | P1 | 92f337637787d615 |
| [07] Spooky (SM) [Scrypts]/Spooky-chart.ssc | 15s | 2m 10s | 2m 36s | 6G | P1 | 7caf253ec7ced10f |
| The Video Boaboaboaboab/The Video Boab Oyedivuth.sm | 15s | 3m 22s | 3m 48s | 6G | P1 | 80a209cf183d62a2 |
| Paradise [R.I.G.H.T.S 2]/Paradise.sm | 15s | 2m 57s | 3m 24s | 6G | P1 | eca0e8a6dc85bfb3 |
| Lower/Lower.ssc | 15s | 1m 57s | 2m 25s | 6G | P1 | 8af44446b364dde5 |
| September/september.ssc | 15s | 2m 24s | 2m 50s | 6G | P1 | 71107cf334c9cab4 |
| Jumper/Jumper.ssc | 15s | 3m 33s | 3m 57s | 6G | P1 | 72ce74211a93b7e2 |
| What If The Whole World Turned Their Swag On/What If The Whole World Turned Their Swag On.ssc | 15s | 2m 15s | 2m 44s | 6G | P1 | 72a647d8f076f839 |
| Actin Up/actinup-fakemines.ssc | 15s | 1m 52s | 2m 20s | 6G | P1 | e8e682256d2a15ea |
| saitama2000/Saitama2000.sm | 15s | 2m 04s | 2m 31s | 6G | P1 | a333ffb33e68608f |
| Delayed Friend Request/Delayed Friend Request.sm | 15s | 2m 04s | 2m 32s | 6G | P1 | 4db2206301a11731 |
| Actin Up/actinup-fakemines.sm | 15s | 1m 52s | 2m 21s | 6G | P1 | 0fc0a6c3e66a51b6 |
| saitama2000/Saitama2000.ssc | 15s | 2m 04s | 2m 31s | 6G | P1 | fb93d41e88000e52 |
| WOP/WOP.ssc | 15s | 2m 58s | 3m 25s | 6G | P1 | f22e86f3df1aa92c |
| Delayed Friend Request/Delayed Friend Request.ssc | 15s | 2m 04s | 2m 33s | 6G | P1 | acce4016ba7c9546 |
| No Tears Left To Cry - [JNero]/No-Tears.sm | 15s | 2m 24s | 2m 54s | 6G | P1 | badd746ba475cd20 |
| ACCENDIO/aCCENDIO.ssc | 16s | 2m 07s | 2m 35s | 6G | P1 | 748c46a0fe0cfb10 |
| Limitless/Limitless.sm | 16s | 1m 58s | 2m 27s | 6G | P1 | 897d282daf6cbb46 |
| Spooky/1.09 - Spooky.sm | 16s | 2m 11s | 2m 38s | 6G | P1 | 3d1de20a3387b5d2 |
| Picture in My Mind [nikko X WINK RMX]/PICTURE IN MY MIND [NIKKO X WINK RMX].ssc | 16s | 2m 08s | 2m 38s | 6G | P1 | ef4e97c53e6ad2d3 |
| Aien-Jihen [Gpop]/Aien-Jihen.ssc | 16s | 2m 37s | 3m 06s | 6G | P1 | fe61b8f708faad87 |
| Limitless/Limitless.ssc | 16s | 1m 58s | 2m 27s | 6G | P1 | 2e769430e7733f8c |
| Rapture/Rapture cut-fakemines.ssc | 16s | 2m 04s | 2m 34s | 6G | P1 | 9d6ecc5033797f49 |
| Save Your Tears/SaveYourTears.ssc | 16s | 3m 07s | 3m 36s | 6G | P1 | e5b5f8e4c0685dd6 |
| Save Your Tears [Cringle Desolation]/SaveYourTears.ssc | 16s | 3m 08s | 3m 37s | 6G | P1 | 8ee29f675e3cf296 |
| chronic latecomer/chronic latecomer.ssc | 16s | 2m 09s | 2m 37s | 6G | P1 | 14eccf0d8fb7cfea |
| [12] Picture in My Mind (SX) [Zaia]/PICTURE IN MY MIND [NIKKO X WINK RMX].ssc | 16s | 2m 08s | 2m 36s | 6G | P1 | 178887137b0b35cf |
| Spooky/1.09 - Spooky.ssc | 16s | 2m 11s | 2m 38s | 6G | P1 | d1f30f122a6e02ff |
| Tamamo no Mae/Tamamo no Mae.ssc | 16s | 2m 09s | 2m 39s | 6G | P1 | a29f5138d450eb61 |
| [T09] Picture in My Mind [nikko X WINK RMX] (SX)/PICTURE IN MY MIND [NIKKO X WINK RMX].ssc | 16s | 2m 07s | 2m 37s | 6G | P1 | 1c60735522914a3d |
| Into The Light2/Into The Light.sm | 16s | 2m 05s | 2m 34s | 6G | P1 | 30ba7e89a631a457 |
| Freaky Deaky/Freaky Deaky.sm | 16s | 3m 41s | 4m 10s | 6G | P1 | 5683ad2aee1ba174 |
| ACCENDIO/aCCENDIO.sm | 16s | 2m 07s | 2m 37s | 6G | P1 | 5835ab911c0c292e |
| Into The Light2/Into The Light.ssc | 16s | 2m 04s | 2m 34s | 6G | P1 | ee89c52b60cc949b |
| Freaky Deaky/Freaky Deaky.ssc | 16s | 3m 41s | 4m 09s | 6G | P1 | cea4505ad4c46562 |
| Jack The Reaper/Jack The Reaper.ssc | 16s | 2m 02s | 2m 32s | 6G | P1 | 4e72d2dc32a08afa |
| Scorpion King [TaroNuke]/scorpion.sm | 16s | 2m 10s | 2m 41s | 6G | P1 | eea1a28876f13bbb |
| REASON for RED/reasonforgay.sm | 16s | 2m 12s | 2m 40s | 6G | P1 | 2612809528eb9628 |
| REASON for RED/reasonforgay.ssc | 16s | 2m 12s | 2m 41s | 6G | P1 | 99a3372a962d49de |
| Biggie Boom Boom/biggie.sm | 16s | 2m 08s | 2m 37s | 6G | P1 | 40b78b4bf42ff35b |
| Jack The Reaper/Jack The Reaper.sm | 17s | 2m 03s | 2m 33s | 6G | P1 | 181e99336e25ef3d |
| Save Your Tears [R.I.G.H.T.S 2]/SaveYourTears.ssc | 17s | 3m 07s | 3m 37s | 6G | P1 | 5a255ba99227582c |
| 100 Bad Days/100 Bad Days.sm | 17s | 2m 23s | 2m 56s | 6G | P1 | 499b11a523835daa |
| Save Your Tears [R.I.G.H.T.S 2]/SaveYourTears.sm | 17s | 3m 08s | 3m 38s | 6G | P1 | bc8753df6828ece2 |
| BBKBBKK/BBKKBKK.ssc | 17s | 2m 21s | 2m 51s | 6G | P1 | 3767741b73c94f99 |
| I'm sorry/sm.ssc | 17s | 2m 43s | 3m 10s | 6G | P1 | 2c6a61d8e963a44b |
| Tear Jerker/tearjerker.ssc | 17s | 2m 13s | 2m 44s | 6G | P1 | 302fa743decaf6cd |
| Save Your Tears [Cringle Desolation]/SaveYourTears.sm | 17s | 3m 09s | 3m 39s | 6G | P1 | af98ee463b8da52a |
| Talk About/talkabout.ssc | 17s | 2m 14s | 2m 44s | 6G | P1 | b627513e67454344 |
| 100 Bad Days/100 Bad Days.ssc | 17s | 2m 23s | 2m 57s | 6G | P1 | f2d9011225df3a8a |
| Biggie Boom Boom/biggie.ssc | 17s | 2m 08s | 2m 38s | 6G | P1 | e34580804dcce96e |
| Turn A - [Freya]/turn_a.ssc | 17s | 2m 10s | 2m 41s | 6G | P2 | becedc74eda050de |
| Tear Jerker/tearjerker.sm | 17s | 2m 12s | 2m 43s | 6G | P1 | 8929124a34915285 |
| Save Your Tears/SaveYourTears.sm | 17s | 3m 08s | 3m 39s | 6G | P1 | e351e499b9b3335f |
| Intro Outro/intro.ssc | 17s | 2m 03s | 2m 31s | 6G | P1 | 1c15b9c1c0e78784 |
| Furst/furst-fakemines.ssc | 17s | 2m 12s | 2m 43s | 6G | P1 | d3d772ec69a779f1 |
| wah-leven [telperion (ddrillini remix)]/eleven.ssc | 17s | 2m 28s | 2m 58s | 6G | P1 | c8f12acf45408c78 |
| Talk About/talkabout.sm | 18s | 2m 14s | 2m 45s | 6G | P1 | 5b4f042e7c597db9 |
| Furst/furst-fakemines.sm | 18s | 2m 13s | 2m 44s | 6G | P1 | af1ceafa8e0893a8 |
| STEVE VERY HARD/STEVE VERY HARD.sm | 18s | 2m 35s | 3m 04s | 6G | P1 | 5e95d2cb0de9eac9 |
| ao no lie/ae no lie.ssc | 18s | 2m 20s | 2m 52s | 6G | P1 | 7147090659266fd1 |
| Ruin Our Friendship/RuinOurFriendship.sm | 18s | 3m 41s | 4m 15s | 6G | P1 | 374eb0da551756a9 |
| panopticon/panopticon.ssc | 18s | 2m 25s | 2m 57s | 6G | P1 | 46615f4d6f6ff7eb |
| Happy Now Remastered/Happy Now.sm | 18s | 3m 43s | 4m 13s | 6G | P2 | e870bbfb00099d8e |
| STEVE VERY HARD/STEVE VERY HARD.ssc | 18s | 2m 37s | 3m 08s | 6G | P1 | dd5f1a41c7a4ae81 |
| Atmosphere/atmosphere-fakemines.sm | 18s | 2m 28s | 3m 01s | 6G | P1 | 9670c8be051802d9 |
| Data Loss/Data_Loss.ssc | 18s | 2m 13s | 2m 45s | 6G | P1 | 7fc068fa297e4205 |
| Ruin Our Friendship/RuinOurFriendship.ssc | 18s | 3m 41s | 4m 17s | 6G | P1 | 07366bc2f7869778 |
| Slamurai/Slamurai.ssc | 18s | 2m 16s | 2m 50s | 6G | P1 | e1b207791087e39a |
| I'm sorry/sm.sm | 18s | 2m 42s | 3m 10s | 6G | P1 | 51701b0b07bd778e |
| Void Virus/Void_Virus.ssc | 18s | 2m 25s | 2m 58s | 6G | P1 | a3d4137a76a6ab62 |
| [11] Slamurai (SX) [Zaia]/Slamurai.ssc | 18s | 2m 16s | 2m 49s | 6G | P1 | 968619db51545b1f |
| Jesus He Knows me/jesusheknowsme.ssc | 18s | 2m 26s | 3m 00s | 6G | P1 | 4457e121432bc005 |
| [T04] Palette Lab (SH)/palette lab.ssc | 18s | 2m 32s | 3m 06s | 6G | P1 | ab809d0fe2109430 |
| ao no lie/ae no lie.sm | 18s | 2m 20s | 2m 52s | 6G | P1 | 49e3acb83ccb5b78 |
| Brain Power - [Cardboard Box]/Brain Power.sm | 18s | 2m 16s | 2m 50s | 42G | P2 | 91cfdcfe801f2621 |
| Happy Now/Happy Now.sm | 18s | 3m 38s | 4m 08s | 6G | P2 | e42e22ef486a712f |
| media offline/media offline.ssc | 18s | 2m 29s | 3m 01s | 6G | P1 | b23cfca53ce4e9e4 |
| Atmosphere/atmosphere-fakemines.ssc | 18s | 2m 28s | 3m 02s | 6G | P1 | 32c38d774442ffc9 |
| OIIA OIIA - [Zaia]/OIIA OIIA.ssc | 18s | 2m 24s | 2m 57s | 6G | P1 | 21300a0b1c8b88cd |
| Toho Mathematics (LADIES CHECK THIS OUT)/thischartsucks.ssc | 18s | 2m 59s | 3m 32s | 6G | P1 | b64f6f3ca7868afe |
| [10] media offline (SM) [Snap]/media offline.ssc | 18s | 2m 29s | 3m 01s | 6G | P1 | e570547f138116bd |
| media offline/media offline.sm | 18s | 2m 29s | 3m 01s | 6G | P1 | 1570024c43db5045 |
| [11] Palette Lab (SH) [Exschwasion]/palette lab.ssc | 19s | 2m 33s | 3m 06s | 6G | P1 | 51c18e50b3f3875d |
| [12] Myths You Forgot (SX) [Benpai &amp; Zaia]/Myths You Forgot.ssc | 19s | 2m 19s | 2m 53s | 6G | P1 | 97ba55ec0e5745da |
| Black Out [Gpop]/Black Out.ssc | 19s | 2m 01s | 2m 36s | 6G | P1 | b511aef83458064b |
| [TLD] Palette Lab/palette lab.ssc | 19s | 2m 33s | 3m 08s | 6G | P1 | 66ca2f4dfd3cef96 |
| Happy Now/Happy Now.ssc | 19s | 3m 38s | 4m 08s | 6G | P2 | 648cae001699309d |
| 319-TECH SOUP-[lv.P.Clark] [Tech Spectrum Super - _TRUE GAMERS CLICK HERE - EXTRA CHARTS]/Venetian Snares - Epidermis.ssc | 19s | 4m 45s | 5m 16s | 6G | P1 | 53397b168dc92640 |
| Happy Now Remastered/Happy Now.ssc | 19s | 3m 43s | 4m 14s | 26G | P2 | c3aff14ffb37944f |
| Watching/watching-fakemines.sm | 19s | 2m 20s | 2m 55s | 6G | P1 | 0c50a14d940d62a1 |
| wndrwll/wndrwll.ssc | 19s | 3m 17s | 3m 52s | 6G | P1 | 27290d9cf304ea4c |
| Jerk/Jerk.ssc | 19s | 2m 25s | 2m 58s | 6G | P1 | 5c1d50fb70534109 |
| Watching/watching-fakemines.ssc | 19s | 2m 20s | 2m 55s | 6G | P1 | a1899c0b34bab9c4 |
| Trancing Pulse (Random)/Trancing Pulse (Random).ssc | 19s | 2m 14s | 2m 49s | 6G | P1 | 9bb9dc4572b75e6f |
| [12] Godspeed (SX) [G. Rosewood]/godspeed.ssc | 19s | 2m 33s | 3m 07s | 6G | P1 | fe5207076483283c |
| mawaru4/mawaru4.ssc | 19s | 3m 10s | 3m 40s | 6G | P1 | a75e8a5cf489385a |
| Remind The Souls/remindthesouls-fakemines.sm | 19s | 2m 32s | 3m 06s | 6G | P1 | 90a9ccde51816f3d |
| Myths You Forgot/Myths You Forgot.ssc | 19s | 2m 19s | 2m 54s | 6G | P1 | bdfbe67f2cd82f65 |
| Bzrp Music Sessions, Volume 53/bzrp53-fakemines.ssc | 19s | 2m 40s | 3m 15s | 6G | P1 | 230a4d90e71ef5fe |
| Final Flash Flight/Final Flash Flight.ssc | 20s | 2m 37s | 3m 12s | 6G | P1 | 6466e125f5567550 |
| Brain Power - [Cardboard Box]/Brain Power.ssc | 20s | 2m 16s | 2m 50s | 6G | P2 | 83441ecafa3cfba6 |
| mawaru4/mawaru4.sm | 20s | 3m 10s | 3m 38s | 6G | P1 | 74d5ad2b8b6dd18a |
| Delightful Day/Delightful Day.ssc | 20s | 3m 47s | 4m 22s | 6G | P1 | f37b389e04396394 |
| The Entity/The Entity.sm | 20s | 2m 11s | 2m 46s | 6G | P1 | c03f6cdcfcb470e0 |
| Remind The Souls/remindthesouls-fakemines.ssc | 20s | 2m 31s | 3m 07s | 6G | P1 | a24b54caef35d4b6 |
| Bzrp Music Sessions, Volume 53/bzrp53-fakemines.sm | 20s | 2m 40s | 3m 16s | 6G | P1 | 950c5203a67250be |
| Lonely/Lonely.ssc | 20s | 4m 13s | 4m 47s | 6G | P1 | f9e03b39bc6c499a |
| Datura -paroxysm-/Datura -paroxysm-.ssc | 20s | 2m 30s | 3m 07s | 6G | P1 | 0af54308fc274e17 |
| Final Flash Flight/Final Flash Flight.sm | 20s | 2m 38s | 3m 13s | 6G | P1 | 4f5866e628b30f73 |
| Girls MIA/girlsmia-fakemines.ssc | 20s | 2m 27s | 3m 02s | 6G | P1 | ef53ee5cf5053183 |
| [09] Delightful Day - (NO CMOD)/Delightful Day.ssc | 20s | 3m 46s | 4m 20s | 6G | P1 | 36f47ba58d2d94d4 |
| Girls MIA/girlsmia-fakemines.sm | 20s | 2m 26s | 3m 01s | 6G | P1 | 2230469fee7221b6 |
| The Entity/The Entity.ssc | 20s | 2m 11s | 2m 46s | 6G | P1 | 8b6d1bed4d9d6c5a |
| Afterburn/Afterburn.ssc | 20s | 2m 44s | 3m 19s | 6G | P1 | bf560ef9fa9b2e27 |
| LeaveTheDoorOpen [R.I.G.H.T.S]/DoorOpen.ssc | 20s | 3m 41s | 4m 17s | 6G | P1 | 6e5a0c4e41ea22fa |
| iLLness LiLin/iLLness LiLin.ssc | 20s | 2m 12s | 2m 47s | 6G | P1 | fddeadb233ca7336 |
| Levels/levels-fakemines.ssc | 20s | 2m 27s | 3m 01s | 6G | P1 | 9aefe627804cba1d |
| Lonely/Lonely.sm | 20s | 4m 14s | 4m 50s | 6G | P1 | 121abf1970e0445f |
| PARTY [pArTy eDiTioN]/Party.ssc | 20s | 2m 14s | 2m 52s | 6G | P1 | 396facf8212c1662 |
| Delightful Day/Delightful Day.sm | 21s | 3m 46s | 4m 23s | 6G | P1 | a31940b5d4b371f3 |
| Dance Robot/dancerobot-fakemines.sm | 21s | 2m 34s | 3m 11s | 6G | P1 | 83826af9e3c61764 |
| Dance Robot/dancerobot-fakemines.ssc | 21s | 2m 34s | 3m 09s | 6G | P1 | ee8f2ffa71460857 |
| broadcast/broadcast.ssc | 21s | 2m 03s | 2m 39s | 6G | P1 | db897615e5dca816 |
| Marvins Room/MarvinsRoom.sm | 21s | 5m 15s | 5m 50s | 6G | P1 | 0d2ad387af101706 |
| FTW/FTW.sm | 21s | 2m 31s | 3m 08s | 6G | P1 | 6272d54848ac9f2b |
| LeaveTheDoorOpen [R.I.G.H.T.S]/DoorOpen.sm | 21s | 3m 41s | 4m 17s | 6G | P1 | 254933d187c2e5a7 |
| Bad Intentions/Bad Intentions.ssc | 21s | 2m 55s | 3m 33s | 6G | P1 | 3e13a7b173ef20e8 |
| Marvins Room/MarvinsRoom.ssc | 21s | 5m 16s | 5m 53s | 6G | P1 | 4b9861dbee80fb24 |
| Selfie - [JNero]/Selfie.ssc | 21s | 2m 42s | 3m 21s | 6G | P1 | a22a74b1ac233827 |
| RUNWAY/RUNWAY.ssc | 21s | 2m 12s | 2m 49s | 6G | P1 | 69ee47d5cf18e4b9 |
| Brain Power (Cranky Remix)/Brain Power (Cranky Remix).ssc | 21s | 2m 11s | 2m 49s | 6G | P1 | ac18ece6891957bd |
| This year, too, we will strive to aim for [Snowfall, Merry Christmas]!!/This year, too, we will strive to aim for [Snowfall, Merry Christmas]!!.ssc | 21s | 3m 44s | 4m 20s | 6G | P1 | 8f56d6a110ddd170 |
| Answers2/Answers.ssc | 21s | 2m 56s | 3m 35s | 6G | P1 | 72e3358afa512712 |
| Ibuprofen and Weed - [Freya]/Ibuprofen and Weed_LEFTS.ssc | 22s | 3m 24s | 3m 59s | 6G | P1 | 03e64ec58cd0c3d9 |
| FTW/FTW.ssc | 22s | 2m 30s | 3m 09s | 6G | P1 | d762994f960c18e5 |
| 319-TECH SOUP-[lv.P.Clark] [Tech Spectrum Super]/Venetian Snares - Epidermis.ssc | 22s | 4m 45s | 5m 19s | 6G | P1 | aa99af5cafb1ccb2 |
| PizzaBoy/PizzaBoy.ssc | 22s | 2m 14s | 2m 47s | 6G | P1 | 66b88be3e6504487 |
| Answers2/Answers.sm | 22s | 2m 57s | 3m 36s | 6G | P1 | ddd18f227e43dced |
| LeaveTheDoorOpen [Cringle Desolation]/DoorOpen.ssc | 22s | 3m 41s | 4m 21s | 6G | P1 | c8d9fd94d9f121bc |
| POP MY SHIT (FOXSKY REMIX)/pop my shit.ssc | 22s | 1m 59s | 2m 37s | 6G | P1 | 9b2705e9fb8f6cc2 |
| [Zaia] Think of a happy place/Think of a happy place.sm | 22s | 3m 23s | 4m 02s | 6G | P1 | aca76cc43087ce34 |
| Potion [Flood_]/Shisui Michiru - Potion (Cut Ver).ssc | 23s | 2m 35s | 3m 16s | 6G | P1 | cdd5dd240d2d527a |
| Think About You/Think About You.ssc | 23s | 3m 40s | 4m 20s | 6G | P1 | 0527941a00855f6e |
| Lip-Sync [Gpop]/Lip-Sync.ssc | 23s | 2m 27s | 3m 08s | 6G | P1 | 85915ca4bac9bb4c |
| Young Dumb And Broke/YDB.ssc | 23s | 3m 22s | 4m 09s | 6G | P2 | cd3de8f3c03c51bc |
| Badlands/Badlands.ssc | 23s | 2m 36s | 3m 17s | 6G | P1 | f865c3fb34a7522c |
| Young Dumb And Broke/YDB.sm | 23s | 3m 22s | 4m 09s | 6G | P2 | ad5a7b90e1897ac2 |
| Think About You/Think About You.sm | 23s | 3m 40s | 4m 22s | 6G | P1 | 6314a40c7ea2b3ce |
| Stuck in the Abyss [DDDAAA]/stuckintheabyss.ssc | 24s | 2m 32s | 3m 14s | 6G | P1 | b50004856eebdd35 |
| Shukusei!! Loli God's Requiem [Gpop]/Shukusei!! Loli God's Requiem.ssc | 24s | 2m 11s | 2m 52s | 6G | P1 | 0ed624d600e4063c |
| Cursed Metamorph - [Zaia]/Cursed Metamorph.ssc | 24s | 2m 32s | 3m 15s | 6G | P1 | 3feb30171c87c384 |
| LeaveTheDoorOpen [Cringle Desolation]/DoorOpen.sm | 25s | 3m 42s | 4m 25s | 6G | P1 | 5e1b59e6d321839b |
| 666/666.ssc | 25s | 2m 14s | 2m 57s | 6G | P1 | 829e94ab82649657 |
| [T08] CO5M1C R4ILR0AD (No CMOD)/CO5M1C R4ILR0AD-chart.ssc | 26s | 2m 33s | 3m 19s | 6G | P1 | 41d8e8f0c6b81aa8 |
| Bamboo/Take.ssc | 26s | 2m 40s | 3m 26s | 6G | P1 | 83334054a83d41f1 |
| 277-MODS-[lv.07] CO5M1C R4ILR0AD/CO5M1C R4ILR0AD-chart.ssc | 26s | 2m 32s | 3m 17s | 6G | P1 | 6966bc05f398f0e8 |
| Pokemon Gym Battle Remix/pokes.ssc | 26s | 3m 01s | 3m 47s | 6G | P1 | 8f40f6c480324919 |
| Circles/Circles.ssc | 26s | 3m 45s | 4m 29s | 6G | P1 | eb4e5c5559461e35 |
| Zoku Shimedore 2000/Zoku Shimedore 2000.ssc | 26s | 2m 22s | 3m 07s | 6G | P1 | 642def061d732288 |
| [11] CO5M1C R4ILR0AD (SH) [TaroNuke vs. Scrypts]/CO5M1C R4ILR0AD-chart.ssc | 26s | 2m 33s | 3m 19s | 6G | P1 | 80fa0154eb89cf78 |
| 273-MODS-[lv.03] [CRYSTAL_ACCESS]/[CRYSTAL_ACCESS].ssc | 27s | 2m 44s | 3m 30s | 6G | P1 | a0707c42970922ef |
| 272-MODS-[lv.02] Riddle/Riddle.ssc | 27s | 2m 40s | 3m 25s | 6G | P1 | d6dba5da60ce8a09 |
| No Role Modelz/No Role Modelz.ssc | 27s | 4m 30s | 5m 13s | 6G | P1 | d678368d153b47c0 |
| [14] [CRYSTAL_ACCESS] (No CMOD) [SX]/[CRYSTAL_ACCESS].ssc | 27s | 2m 45s | 3m 32s | 6G | P1 | 1275a659b0dc21d2 |
| [CRYSTAL_ACCESS]/[CRYSTAL_ACCESS].sm | 27s | 2m 43s | 3m 29s | 6G | P1 | 59e4ca9e369aa975 |
| Paradise [R.I.G.H.T.S 2]/Paradise.ssc | 27s | 2m 58s | 3m 39s | 6G | P1 | f66b808b28f70200 |
| [11] Nishi-Shinjuku seisou kyoku (SX) [Scrypts]/nssk-chart.ssc | 27s | 2m 04s | 2m 51s | 6G | P1 | ecb7f9f9a8fb340b |
| 276-MODS-[lv.06] Nishi-Shinjuku seisou kyoku/nssk-chart.ssc | 27s | 2m 04s | 2m 50s | 6G | P1 | 6e5c6b63ff10a521 |
| Astrogirl [wrsw]/Astrogirl.ssc | 28s | 2m 15s | 3m 04s | 6G | P1 | dce383bd8964e8f5 |
| Circles/Circles.sm | 28s | 3m 45s | 4m 31s | 6G | P1 | ccfbbe2824310517 |
| Riddle/Riddle.ssc | 28s | 2m 40s | 3m 26s | 6G | P1 | f8c3155bad6d698e |
| Paradise/Paradise.ssc | 28s | 2m 58s | 3m 38s | 6G | P1 | 6a7674e03615eb2e |
| [CRYSTAL_ACCESS]/[CRYSTAL_ACCESS].ssc | 28s | 2m 44s | 3m 31s | 6G | P1 | f318c83aaebd5b06 |
| Paradise [Cringle Desolation]/Paradise.ssc | 28s | 2m 58s | 3m 38s | 6G | P1 | 391c7f4f57c3f707 |
| Dreams Bloom After School/Dreams Bloom After School.ssc | 28s | 2m 58s | 3m 39s | 26G | P2 | 798ceb1db0a936b4 |
| Get Into It/GetIntoIt.sm | 28s | 2m 19s | 3m 01s | 6G | P2 | bbd73a8be292d1aa |
| Chewingood!!!/Chewingood!!!.ssc | 28s | 2m 12s | 3m 01s | 6G | P1 | d68dae09d4a90259 |
| PO (wrashi Bootleg) [Gpop]/PO (wrashi Bootleg).ssc | 28s | 2m 46s | 3m 34s | 6G | P1 | 1a32bf7c4855ba84 |
| [10] Riddle (DX) [Brother Mojo remixes A. Astral]/Riddle.ssc | 28s | 2m 41s | 3m 29s | 6G | P1 | 93fa9acba23998b8 |
| [10] Riddle (No CMOD) [SX]/Riddle.ssc | 28s | 2m 41s | 3m 28s | 6G | P1 | debc9269c5a14e1e |
| 280-MODS-[MASTER] Sharkmode/Sharkmode.ssc | 29s | 2m 36s | 3m 22s | 6G | P2 | 68eda87bf02562c3 |
| Get Into It/GetIntoIt.ssc | 29s | 2m 19s | 3m 00s | 6G | P2 | 5e922ad5ae24e720 |
| Molly/Molly.sm | 29s | 5m 36s | 6m 34s | 6G | P1 | 553b63370b0f16d7 |
| Spectrum Sequence/spectrumsequence.ssc | 29s | 2m 38s | 3m 26s | 6G | P1 | a7d381a3d24f6b30 |
| paw, paw!/paw paw.ssc | 29s | 2m 30s | 3m 19s | 6G | P1 | a002cc9c452c66dc |
| [09] Spectrum Sequence (SH) [DRILLBOT vs. valgrind]/spectrumsequence.ssc | 29s | 2m 37s | 3m 25s | 6G | P1 | 2d589a455fd8d5b1 |
| The Scale/The Scale.ssc | 29s | 2m 49s | 3m 40s | 6G | P1 | eebba508ee246ebe |
| negator/NEGATOR.sm | 29s | 2m 28s | 3m 22s | 6G | P1 | 1dc6d2f045899152 |
| Sharkmode [Ky_Dash]/Sharkmode.ssc | 29s | 2m 38s | 3m 23s | 6G | P2 | 730650ffb42269d8 |
| Toki o Kizamu Uta (Nhato Remix)/Toki o Kizamu Uta (Nhato Remix).ssc | 29s | 3m 22s | 4m 12s | 6G | P1 | 74d3e8ea728e2d24 |
| Molly/Molly.ssc | 30s | 5m 36s | 6m 33s | 6G | P1 | 689df515d31d7415 |

### 30–60 seconds

| Song simfile | Replay | Capture | Fresh stages | Replay cap | Timing | Case ID |
| --- | --- | --- | --- | --- | --- | --- |
| mawaru3/mawaru3.sm | 30s | 4m 15s | 4m 56s | 6G | P1 | f092ae91d59eb56e |
| mawaru5/mawaru5.sm | 30s | 4m 18s | 4m 59s | 6G | P1 | 33e246a6cecf7734 |
| Apollo/Apollo.ssc | 31s | 2m 57s | 3m 48s | 6G | P2 | ccab525f9b554b84 |
| Apollo/Apollo.sm | 31s | 2m 57s | 3m 49s | 6G | P2 | ba1dd6297cd6aae0 |
| I (Ai)/I (Ai).ssc | 32s | 2m 20s | 3m 10s | 6G | P1 | e6454e59004cbdac |
| Collaboration with Paul J Kim/Something.sm | 32s | 2m 34s | 3m 28s | 6G | P1 | 5c63f1e940a14e50 |
| Deceive Your Insight [TaroNuke]/insight.ssc | 32s | 2m 16s | 3m 15s | 6G | P1 | 495f6b72800850ce |
| Megalovania SM5 [TaroNuke]/megalovania.ssc | 32s | 3m 44s | 4m 34s | 6G | P1 | 6d6b017fdf7768bf |
| Trinity Field/Trinity Field.ssc | 33s | 2m 37s | 3m 36s | 6G | P1 | bea2ae5a98663f53 |
| [FULL SONG] Stuck in the Abyss [DDDAAA]/stuckintheabyss.ssc | 33s | 3m 39s | 4m 36s | 6G | P1 | 80df72260b891d5c |
| [11] Gemini in Clockland/Gemini in Clockland.ssc | 33s | 2m 44s | 3m 41s | 6G | P1 | 0670331e3bdf3e73 |
| Gemini in Clockland/Gemini in Clockland.ssc | 34s | 2m 44s | 3m 42s | 6G | P1 | 54f5eaec5cdcab5c |
| See Tinh/See Tinh.ssc | 35s | 3m 10s | 4m 10s | 6G | P1 | bf7c3d6abcadb7d2 |
| Beauty in chaos/Beauty in Chaos.ssc | 35s | 4m 44s | 5m 41s | 6G | P1 | 7b3c29bd80d5c994 |
| SPLAK IT DOWN - [Zaia +ruunix2]/SPLAK IT DOWN.ssc | 36s | 2m 09s | 3m 08s | 6G | P1 | 47ff4627cbdc3c90 |
| See Tinh/See Tinh.sm | 36s | 3m 09s | 4m 11s | 6G | P1 | 037516ce03a76db7 |
| (R5) Let Me Hear That/let me hear that.sm | 38s | 2m 51s | 3m 55s | 6G | P1 | e712d4cde3f651c0 |
| Datamania (tpz Overheat Remix)/Datamania (tpz Overheat Remix).ssc | 38s | 2m 34s | 3m 38s | 6G | P1 | 81ff7d5029833825 |
| [11] Let Me Hear That (SX) [TaroNuke]/let me hear that.ssc | 38s | 2m 52s | 3m 55s | 6G | P1 | d39db4487275ec0b |
| Beauty in chaos/Beauty in Chaos.sm | 38s | 4m 44s | 5m 44s | 6G | P1 | 225f82cdd3962f8b |
| Step Your Game Up (Director's Cut)/stepyourgameup.ssc | 39s | 2m 51s | 3m 53s | 6G | P1 | f632e44ca4622de9 |
| Metronogik/Song.ssc | 40s | 2m 50s | 3m 50s | 6G | P2 | bd062750cefe5be7 |
| [09] LALA (SH) [Exschwasion]/lala.ssc | 40s | 2m 46s | 3m 52s | 6G | P1 | 2963fe5a4b3cb75f |
| DREAMING-ING!!/DREAMING-ING!!.ssc | 40s | 1m 21s | 2m 28s | 26G | P2 | 7666d9897cac1286 |
| [12] bunny-house - (No CMOD)/steps.ssc | 41s | 2m 55s | 4m 00s | 6G | P1 | 0c4fd601f2ef7723 |
| [TPE2] LALA/lala.ssc | 41s | 2m 47s | 3m 52s | 6G | P1 | 09e38a61f0a0655d |
| LALA/lala.ssc | 41s | 2m 45s | 3m 50s | 6G | P1 | 66b0dc036b382ca1 |
| assgore/goatdad.ssc | 42s | 3m 39s | 4m 48s | 6G | P1 | b7fac2195ecc844c |
| [FULL SONG] Kagetsu no Yume [wrsw]/Kagetsu no Yume.ssc | 42s | 4m 09s | 5m 23s | 6G | P1 | 1734bd975264309b |
| [F]FS+BR(lv.9) Bunny House/steps.sm | 42s | 2m 56s | 4m 02s | 6G | P1 | f5e5675b35ce56c7 |
| Invert/invert.sm | 42s | 5m 53s | 7m 01s | 6G | P1 | 963cb9b48abd33f1 |
| [08] And Drugs - (NO CMOD)/and drugs.ssc | 43s | 2m 31s | 3m 38s | 6G | P1 | 2251ef83c6bd065f |
| [Zaia] I'm For You/I'm For You.ssc | 43s | 4m 06s | 5m 15s | 6G | P1 | b838520586608049 |
| [F]FS+BR(lv.9) Bunny House/steps.ssc | 43s | 2m 56s | 4m 04s | 6G | P1 | 09c6c5c4aea71b12 |
| bunny-house/steps.sm | 43s | 2m 56s | 4m 05s | 6G | P1 | 91157d0fee9e2d0d |
| 278-MODS-[lv.08] And Drugs/and drugs.ssc | 43s | 2m 32s | 3m 40s | 6G | P1 | abe694267a1522a8 |
| [12] And Drugs (No CMOD) [SX]/and drugs.ssc | 44s | 2m 33s | 3m 40s | 6G | P1 | 280894a7047d9c66 |
| And Drugs/and drugs.ssc | 44s | 2m 33s | 3m 41s | 6G | P1 | 28d1ad2d37e533c2 |
| And Drugs/and drugs.sm | 45s | 2m 31s | 3m 40s | 6G | P1 | 9d67ef44a2ab1f4d |
| 275-MODS-[lv.05] BroGamer/BroGamer.ssc | 45s | 2m 32s | 3m 42s | 6G | P1 | f2deebaeb2c3a46f |
| [13] Flying Castle/flying castle.ssc | 46s | 2m 31s | 3m 42s | 6G | P1 | d6c331dcba96997d |
| [N]TECH SOUP(MASTER) Flying Castle/flying castle.sm | 46s | 2m 29s | 3m 40s | 6G | P1 | cdadde08ea8260ec |
| Flying Castle/flying castle.sm | 46s | 2m 29s | 3m 41s | 6G | P1 | 4db17411c26c5ddd |
| BroGamer/BroGamer.ssc | 46s | 2m 33s | 3m 46s | 6G | P1 | 336a094a26543598 |
| Invert/invert.ssc | 46s | 5m 54s | 7m 05s | 6G | P1 | 5efb979a786b09fa |
| Flying Castle/flying castle.ssc | 47s | 2m 30s | 3m 42s | 6G | P1 | f9d2e317f4326687 |
| [N]TECH SOUP(MASTER) Flying Castle/flying castle.ssc | 47s | 2m 31s | 3m 44s | 6G | P1 | 4b090d6b43566dd6 |
| (R10) Warp Zone/warp zone.ssc | 47s | 3m 06s | 4m 27s | 6G | P1 | af4e305b129581cc |
| 274-MODS-[lv.04] SAIKYOU STRONGER/REDALiCE_vs_USAO_-_STRONGER.ssc | 48s | 2m 46s | 3m 57s | 6G | P2 | 935b7152e8f43749 |
| Koi [UPS2016]/koi.ssc | 48s | 3m 30s | 4m 26s | 6G | P1 | 4090b2e03f844a05 |
| Popek feat. Titans Fall Harder - Downfall/Downfall.ssc | 49s | 5m 11s | 6m 32s | 6G | P1 | 24a06dae4599dd64 |
| [07] 7th Gear - (No CMOD)/7th Gear.ssc | 50s | 2m 36s | 3m 50s | 6G | P1 | 47c6af4ffb388363 |
| E2/E.sm | 50s | 2m 17s | 3m 45s | 6G | P1 | c66f9f26050402e8 |
| LORELEI/LORELEI.ssc | 50s | 3m 50s | 5m 08s | 6G | P1 | 8e003952da1ece2b |
| 7th Gear/7th Gear.ssc | 51s | 2m 36s | 3m 52s | 6G | P1 | fb15b1d8e22c2e32 |
| Loop/loop.ssc | 51s | 2m 43s | 4m 09s | 6G | P1 | f38a2b418ee7b043 |
| tamashi/tamashi.sm | 52s | 3m 05s | 4m 43s | 6G | P1 | c02cf9153c836efc |
| Koi [UPS2016]/koi.sm | 52s | 3m 30s | 4m 31s | 6G | P1 | 0baadb00ca5b32fc |
| Spectrum (Odyssey's Prism Mix) [Telperion]/spectrod.ssc | 54s | 3m 56s | 5m 15s | 6G | P2 | 74d97529575b9032 |
| 321STARS/321STARS.ssc | 55s | 2m 05s | 3m 41s | 6G | P1 | fc41299deb0561e8 |
| Lake of Lost Nostalgia/Lake of Lost Nostalgia.ssc | 56s | 2m 42s | 4m 07s | 6G | P1 | b5fb9f5437f0cc08 |
| E2/E.ssc | 57s | 2m 20s | 3m 55s | 6G | P1 | a328e6a6a680b57a |
| [10] Lake of Lost Nostalgia (SX) [Ky_Dash]/Lake of Lost Nostalgia.ssc | 57s | 2m 42s | 4m 09s | 6G | P1 | b8e0bb0687ef429e |
| Gangu Kyousou Kyoku -Shuuen-/chart.ssc | 58s | 3m 08s | 4m 47s | 6G | P1 | e381d04b2fe57f84 |

### 1–3 minutes

| Song simfile | Replay | Capture | Fresh stages | Replay cap | Timing | Case ID |
| --- | --- | --- | --- | --- | --- | --- |
| Space Creation Theory/space creation theory.ssc | 1m 01s | 3m 02s | 4m 40s | 6G | P1 | 93d4cdfb2970d034 |
| finite/sta - Finite.sm | 1m 02s | 2m 27s | 4m 05s | 6G | P1 | 70dc4f4e99392381 |
| Anzu no Uta (U.P.S.)/Anzu no Uta.sm | 1m 03s | 3m 02s | 4m 45s | 6G | P2 | a5df4e3b38df280f |
| Gallium Phosphide/Gallium Phosphide.ssc | 1m 04s | 2m 54s | 4m 41s | 26G | P1 | 300e86e379344389 |
| The Great Divide - [Axis, PCBoyGames]/The_Great_Divide_Seven_Lions_Remix_-_Velvetine_141_BPM.sm | 1m 05s | 4m 23s | 6m 25s | 26G | P1 | bdabd7d478d076be |
| The Great Divide - [Axis, PCBoyGames]/The_Great_Divide_Seven_Lions_Remix_-_Velvetine_141_BPM.ssc | 1m 07s | 4m 21s | 6m 24s | 26G | P1 | 21eaa41a3c242538 |
| 279-MODS-[lv.09] Karachi/Jorts - Karachi.ssc | 1m 07s | 2m 41s | 4m 22s | 6G | P1 | 9c845cae6edaa4c6 |
| Karachi/Jorts - Karachi.ssc | 1m 09s | 2m 41s | 4m 24s | 6G | P1 | ee05076a40d0a9af |
| Igaku/Igaku.ssc | 1m 09s | 2m 55s | 4m 58s | 26G | P1 | 5a6e876c367384dc |
| Igaku/Igaku.sm | 1m 11s | 2m 57s | 5m 02s | 26G | P1 | 128d63c6c33d4cb4 |
| Oshama Scramble! (Cranky Remix)/Oshama Scramble! (Cranky Remix).ssc | 1m 11s | 3m 03s | 4m 57s | 26G | P1 | 62f7a478097081e5 |
| HOPE/HOPE.ssc | 1m 12s | 3m 06s | 5m 04s | 6G | P1 | b935bd6b6a662d01 |
| THE WORLD REVOLVING [TaroNuke]/steps.sm | 1m 12s | 2m 50s | 4m 50s | 42G | P2 | cdb3faa216e1adfc |
| THE WORLD REVOLVING [TaroNuke]/steps.ssc | 1m 13s | 2m 49s | 4m 51s | 6G | P2 | 2ac31dad727e6303 |
| Ultimate taste/Ultimate taste.ssc | 1m 14s | 4m 51s | 6m 36s | 6G | P1 | 06243f34daf1c8ae |
| Godspeed [TaroNuke]/godspeed.sm | 1m 15s | 2m 57s | 5m 08s | 26G | P1 | 34658d32935856e2 |
| Someone Special - hubert/Someone Special.sm | 1m 16s | 3m 19s | 5m 27s | 26G | P1 | e2aad032b60853c4 |
| U-0 - [PCBoyGames]/Srezcat - U-0.ssc | 1m 19s | 4m 04s | 6m 31s | 26G | P1 | ae9d75910258857a |
| Someone Special - hubert/Someone Special.ssc | 1m 19s | 3m 25s | 5m 40s | 26G | P1 | 4b0150e9f9595e06 |
| Cold/Cold.ssc | 1m 31s | 3m 44s | 6m 25s | 26G | P1 | 30bd12a3a8b6302a |
| Chipsqueak/chipsqueak.sm | 1m 34s | 2m 38s | 5m 28s | 26G | P1 | 1e5fae5bb7c02f97 |
| Chipsqueak/chipsqueak.ssc | 1m 35s | 2m 41s | 5m 31s | 26G | P1 | 5f7ffff1f1a85dec |
| Rayc Fire 2 (SM5)/Rayc Fire 2.ssc | 1m 37s | 3m 47s | 6m 30s | 26G | P1 | 43d599e70839d1b5 |
| Bad Trails/Maybe it was fated.sm | 1m 38s | 2m 42s | 4m 28s | 6G | P1 | 5cbc2bfa91cfbe0b |
| mawaru6/mawaru6.sm | 1m 39s | 5m 15s | 7m 51s | 26G | P1 | 33094275d983528c |
| 99+ [-YOSEFU-]/99+.ssc | 1m 41s | 2m 59s | 5m 42s | 26G | P2 | d3aa73c0f2f94a22 |
| Shakunetsu2 [TaroNuke]/shakunetsu2.sm | 1m 42s | 3m 21s | 6m 16s | 26G | P1 | 6a3f4f26b2753004 |
| Bad Trails/Maybe it was fated.ssc | 1m 42s | 2m 42s | 4m 32s | 6G | P1 | 6ea6105f433bbd84 |
| kaboooooom!/KABOOOOOM!!!!.sm | 1m 50s | 4m 37s | 7m 41s | 26G | P1 | d9e2e362f6f34713 |
| Planet Calling/Planet Calling.ssc | 1m 51s | 3m 11s | 6m 20s | 26G | P1 | 255308d88d7d6605 |
| kaboooooom!/KABOOOOOM!!!!.ssc | 1m 52s | 4m 41s | 7m 46s | 26G | P1 | cfa9d731a57116f9 |
| 303-MODS-[lv.memes] [Tech Spectrum Super - _TRUE GAMERS CLICK HERE - EXTRA CHARTS]/KABOOOOOM!!!!.ssc | 1m 53s | 4m 39s | 7m 46s | 26G | P1 | 70a79b979b3df07b |
| Rayc Fire 2 (SM5)/Rayc Fire 2.sm | 1m 54s | 3m 36s | 6m 35s | 26G | P1 | 199056062f473784 |
| Shooting Love/Shooting Love.ssc | 1m 55s | 3m 54s | 7m 09s | 26G | P1 | 161f4d2f8468456f |
| [FULL SONG] Shukusei!! Loli God's Requiem [Gpop]/Shukusei!! Loli God's Requiem.ssc | 1m 55s | 5m 55s | 8m 58s | 26G | P1 | e94e772c9c642cc1 |
| 303-MODS-[lv.memes] [Tech Spectrum Super]/KABOOOOOM!!!!.ssc | 1m 56s | 4m 43s | 7m 57s | 26G | P1 | 24458e3958de1437 |
| Quarantine/Quarantine.ssc | 2m 03s | 4m 55s | 8m 24s | 26G | P1 | d5dd73d900ac422a |
| Flowers [Cringle Desolation]/Flowers.ssc | 2m 03s | 4m 42s | 8m 06s | 26G | P1 | 9659e504da711b43 |
| Quarantine/Quarantine.sm | 2m 04s | 4m 47s | 8m 10s | 26G | P2 | 898f3b171ed333ed |
| (R6) Waltz Capriccio/waltz_capriccio.ssc | 2m 09s | 4m 03s | 7m 43s | 26G | P1 | 4de9b431020a116f |
| mawaru8/mawaru8.sm | 2m 12s | 5m 31s | 8m 42s | 26G | P2 | 3ed87baea8fc010d |
| feelyourtouch e.d.e.n/feelyourtouch eden.ssc | 2m 19s | 3m 43s | 7m 35s | 26G | P1 | df77da725142dca5 |
| Dongo Bongo/dongobongo2.ssc | 2m 22s | 4m 57s | 8m 59s | 26G | P1 | 2c9db316dfcd9ab2 |
| Shivers/Shivers.ssc | 2m 39s | 4m 53s | 9m 26s | 26G | P1 | 49ec0d0c00dfc584 |
| Shivers/Shivers.sm | 2m 40s | 4m 57s | 9m 29s | 26G | P1 | 83dd6e5b0d55c8ae |
| [09] Who the Hell Is Edgar (SX) [Telperion]/Who the Hell Is Edgar.ssc | 2m 44s | 4m 44s | 9m 22s | 26G | P1 | 4f4295d0ebf3f89d |
| [10] flip69 (DX) [Telperion]/flip69.ssc | 2m 44s | 4m 15s | 8m 49s | 26G | P1 | c17d988fdfa4949d |
| Who The Hell Is Edgar/Who the Hell Is Edgar.ssc | 2m 51s | 4m 45s | 9m 32s | 26G | P1 | b43c3fe283366b02 |
| [14] [Zaia] I_m For You/I_m For You.ssc | 2m 53s | 5m 23s | 10m 05s | 26G | P1 | 750815a1a10fd90a |
| Crazy Crazy/Crazy Crazy.ssc | 2m 56s | 4m 47s | 9m 47s | 26G | P2 | ade709b3e4efeb3a |
| Goodbye/Goodbye.ssc | 2m 57s | 4m 06s | 9m 09s | 26G | P1 | 6a5cc91dd2a10862 |

### 3–10 minutes

| Song simfile | Replay | Capture | Fresh stages | Replay cap | Timing | Case ID |
| --- | --- | --- | --- | --- | --- | --- |
| Butterfly by DDR/buttchew.ssc | 3m 35s | 5m 03s | 11m 05s | 26G | P1 | eb7d5a89defeeb31 |
| Cuphead [TaroNuke]/botanic.sm | 3m 41s | 6m 23s | 12m 30s | 42G | P2 | 10fe9862c1cf88c3 |
| Cloud99 (As Above Mix)/Song.ssc | 3m 54s | 7m 07s | 14m 05s | 26G | P2 | aa110bbb4b97b8a4 |
| Raving With Fire/Raving With Fire.ssc | 4m 10s | 6m 17s | 13m 17s | 26G | P1 | b7d3c53da9a1e2c7 |
| Raving With Fire/Raving With Fire.sm | 4m 15s | 6m 25s | 13m 31s | 26G | P1 | 9bb0eb4860a33838 |
| Mamono/sm.sm | 4m 18s | 3m 36s | 8m 03s | 26G | P1 | 85a120c688e14906 |
| mawaru7/mawaru7.sm | 4m 42s | 8m 08s | 15m 36s | 42G | P2 | 7a0708216dd461ad |
| What A Wonderful World/WAWW.sm | 5m 02s | 7m 53s | 16m 44s | 42G | P2 | 7fa17005f2a1fbae |
| Paint the Town Red/PaintTheTownRed.sm | 6m 07s | 7m 56s | 17m 16s | 50G | P2 | 272cbdbb21a302b2 |
| Paint the Town Red/PaintTheTownRed.ssc | 6m 20s | 8m 03s | 17m 40s | 50G | P2 | 6a3e1a6f93bdc9fc |
| mawaru9/mawaru9.sm | 6m 34s | 6m 28s | 14m 12s | 26G | P2 | 02d24424431a0192 |
| fof_guys/fof.ssc | 7m 35s | 11m 22s | 25m 19s | 50G | P2 | e115c0f3019c18b4 |

### 10 minutes or more

| Song simfile | Replay | Capture | Fresh stages | Replay cap | Timing | Case ID |
| --- | --- | --- | --- | --- | --- | --- |
| mr sandman/mr sandman.sm | 13m 52s | 4m 09s | 19m 23s | 42G | P2 | 9a7dc9dd696c05ad |

## Sources and refresh method

- [First-audit measurements](proxmox-audit-2026-11-15/all-results.json), including nested `resource_recheck` and `dependency_recheck` records.
- [Repair-pass captures](proxmox-pass2-2026-11-15/primary-attempts.json), [additional attempts](proxmox-pass2-2026-11-15/extra-attempts.json), and [final replays](proxmox-pass2-2026-11-15/final-replays.json).
- [November 15 primary ledger](proxmox-pass2-2026-11-15/case-ledger.json), [failure explanations](proxmox-pass2-2026-11-15/README.md), [source revisions](proxmox-pass2-2026-11-15/repository-pins.json), and [accepted archive hashes](proxmox-pass2-2026-11-15/published-archives.json).
- [November 16 captures](proxmox-pass3-2026-11-16/native-attempts.json), [replays](proxmox-pass3-2026-11-16/replays.json), [ArrowQuest resource replays](proxmox-pass3-2026-11-16/arrow-resource-replays.json), and [latest published primary ledger](proxmox-pass3-2026-11-16/case-ledger.json).
- [Repeated heavy-fixture profiles](proxmox-pass3-2026-11-16/profiles/README.md): Mr Sandman 13m 23s–13m 29s, Paint SSC 6m 20s–6m 21s, and fof 8m 05s–8m 14s. These include profiler overhead and stay separate from the correctness-run measurements.

Timings come from `stages.<stage>.elapsed_seconds`, rounded to the nearest second. Do not use `estimated_song_seconds` as replay cost, timeout limits as measured durations, or aggregate `started_at`/`finished_at` across unrelated retries. P2 replay/capture pairs are matched by decoded archive SHA-256. Historical successful replay stages include nested rechecks; missing complete capture/pack timings remain unknown. Retry IDs ending in `-memory26` are grouped under their original case/profile ID. This document does not average different revisions or profiles together.

When future targeted runs produce reports, update just their measurements and provenance here. No full-corpus rerun is needed to maintain this guide.
