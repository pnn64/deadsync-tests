# Five-chart song-Lua coverage

Generated 2026-11-20T07:38:14.334706+00:00. Final replay stage: after01.

Exactly five previously failing song charts were selected. Each fresh native archive was replayed through diagnostic Lua and production gameplay paths. The original Circles before/after reference uses the same selected chart and is excluded from the five-chart totals.

Original mismatch entries come from the failure ledger. Fresh native frame cadence can differ, so a zero fresh-baseline count does not establish reproduction of the old timing failure. Only the original Circles reference was replayed before and after this fix; the other four original failure counts are historical evidence. The sum of 136 historical entries is not a claim that all 136 were replayed and removed. Mismatch counts are retained report entries; draw mismatch counters are reported separately.

| Chart | Case | Original frames | Original entries | Fresh baseline entries | Final entries | Final errors | Final native / D / P frames |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Nishi-Shinjuku seisou kyoku | ecb7f9f9a8fb340b-c0001 | 1648 | 10 | 0 | 0 | 0 | 2093 / 2093 / 2093 |
| Circles (native title Episode 15) | ccfbbe2824310517-c0001 | 2483 | 12 | 0 | 0 | 0 | 2822 / 2822 / 2822 |
| [CRYSTAL_ACCESS] | 1275a659b0dc21d2-c0001 | 1683 | 20 | 0 | 0 | 0 | 2385 / 2385 / 2385 |
| And Drugs | abe694267a1522a8-c0001 | 1493 | 46 | 0 | 0 | 0 | 1689 / 1689 / 1689 |
| Flying Castle | cdadde08ea8260ec-c0001 | 1488 | 48 | 54 | 0 | 0 | 1754 / 1754 / 1754 |

All five select chart index 1, dance versus, Challenge. Exact identities:

| Chart | Native title | Source simfile | Selected description |
| --- | --- | --- | --- |
| Nishi-Shinjuku seisou kyoku | [5813] [11] 西新宿清掃曲 (No CMOD) | [11] Nishi-Shinjuku seisou kyoku (SX) [Scrypts]/nssk-chart.ssc | [FX] DS+, XO+, KS, SJ |
| Circles (native title Episode 15) | Episode 15 Circles | Circles/Circles.sm |  |
| [CRYSTAL_ACCESS] | [14] [CRYSTAL_ACCESS] (No CMOD) | [14] [CRYSTAL_ACCESS] (No CMOD) [SX]/[CRYSTAL_ACCESS].ssc | [FX] BR+ BS BU FS+ XO |
| And Drugs | 278\|MODS\|[lv.08] And Drugs↑↑ | 278-MODS-[lv.08] And Drugs/and drugs.ssc | [FX] XMOD XO FS+ BR+ SS DS DT BU |
| Flying Castle | [N]TECH SOUP(MASTER) Flying Castle | [N]TECH SOUP(MASTER) Flying Castle/flying castle.sm | lapix get iphone |

D means diagnostic; P means production. Native frames count once per archive. Each path performs its own stage, draw, vertex and text comparisons. Production command/query instrumentation is pending, so its query count is unavailable.

| Chart | Path | Stage fields | Stage samples | Draws | Vertices | Text | Random replayed / captured | Queries actual / native | Inputs | Draw mismatches | Retained entries | Errors |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Nishi-Shinjuku seisou kyoku | D | 10718 | 119 | 482 | 2892 | 0 | 231 / 231 | 160000 / 160000 | 0 | 0 | 0 | 0 |
| Nishi-Shinjuku seisou kyoku | P | 10718 | 119 | 482 | 2892 | 0 | 231 / 231 | not reported | 0 | 0 | 0 | 0 |
| Circles (native title Episode 15) | D | 16806 | 218 | 19110 | 114660 | 0 | 0 / 0 | 95277 / 95277 | 0 | 0 | 0 | 0 |
| Circles (native title Episode 15) | P | 16806 | 218 | 19110 | 114660 | 0 | 0 / 0 | not reported | 0 | 0 | 0 | 0 |
| [CRYSTAL_ACCESS] | D | 12911 | 154 | 0 | 0 | 0 | 0 / 0 | 202052 / 202052 | 0 | 0 | 0 | 0 |
| [CRYSTAL_ACCESS] | P | 12911 | 154 | 0 | 0 | 0 | 0 / 0 | not reported | 0 | 0 | 0 | 0 |
| And Drugs | D | 10275 | 138 | 0 | 0 | 0 | 0 / 0 | 243793 / 243793 | 0 | 0 | 0 | 0 |
| And Drugs | P | 10275 | 138 | 0 | 0 | 0 | 0 / 0 | not reported | 0 | 0 | 0 | 0 |
| Flying Castle | D | 10160 | 130 | 0 | 0 | 0 | 0 / 0 | 319583 / 319583 | 0 | 0 | 0 | 0 |
| Flying Castle | P | 10160 | 130 | 0 | 0 | 0 | 0 / 0 | not reported | 0 | 0 | 0 | 0 |

Five fresh archive totals:

| Measure | Diagnostic | Production |
| --- | --- | --- |
| native_frames | 10743 | 10743 |
| replayed_frames | 10743 | 10743 |
| checked_stage_samples | 759 | 759 |
| compared_stage_fields | 60870 | 60870 |
| draw_samples_compared | 19592 | 19592 |
| submitted_vertices_compared | 117552 | 117552 |
| live_text_samples_compared | 0 | 0 |
| input_events_replayed | 0 | 0 |
| render_random_inputs_replayed | 231 | 231 |
| render_random_inputs_captured | 231 | 231 |
| unreplayed_render_random_inputs | 0 | 0 |
| draw_mismatches | 0 | 0 |
| typed_equal_backing_aft_uv_samples_compared | 0 | 0 |
| uncompared_owned_immediate_draws | 0 | 0 |
| uncompared_owned_normal_draws | 0 | 0 |
| command_queries_native_count | 1020705 | not reported |
| command_queries_actual_count | 1020705 | not reported |
| retained_mismatch_entries | 0 | 0 |
| errors | 0 | 0 |

Acceptance flags are copied literally. Root archive_accepted is the combined comparator decision; nested production archive_accepted is a separate, stricter flag. Neither replaces the production, whole-song or pixel parity proof flags. All root and nested booleans are retained in coverage.json.

| Chart | Root accepted | D checks | P checks | Root interactive checks | P accepted | Production parity | Whole-song parity | Pixel parity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Nishi-Shinjuku seisou kyoku | true | true | true | false | false | false | false | false |
| Circles (native title Episode 15) | true | true | true | false | false | false | false | false |
| [CRYSTAL_ACCESS] | true | true | true | false | false | false | false | false |
| And Drugs | true | true | true | false | false | false | false | false |
| Flying Castle | true | true | true | false | false | false | false | false |

## Original Circles reference

Both runs use compressed archive SHA256 1467b5bccb06fe84d622d5590f5ee732dfbd6ed0b4fcbf9af7036f37d9b2a38e. This preserves the original frame sequence.

| Run | Native / D / P frames | D entries | P entries | Errors | Root accepted |
| --- | --- | --- | --- | --- | --- |
| Baseline | 2483 / 2483 / 2483 | 12 | 0 | 0 | false |
| Final | 2483 / 2483 / 2483 | 0 | 0 | 0 | true |

Native Player.cpp refills autoplay rolls, processes active holds, then crosses autoplay rows. The fix puts live dance autoplay hold processing before new row judgments and removes the global row-triggered settlement path. Physical input and recorded input replay retain their existing event-time integration; Pump retains its checkpoint path. Same-column active-hold replacement retains immediate replacement settlement; these five charts do not establish general parity for that separate edge.

## Regression evidence

The initial full-frame short-hold regression failed before the fix: Some(Held) was observed where None was required at the end of the update that crossed the hold's head and tail (1 failed, 0 passed; cargo exit 101). The final test adds a later crossed tap and covers Single and Versus. The focused selection executed 46 individual tests: 46 passed, 0 failed, 0 ignored. The roll regression runs full gameplay frames for dance and Pump at four rates. The final replay build is bound to the same five gameplay source hashes as the focused test receipt.

## Recorded formatting checks

The package check (cargo fmt -p deadsync-gameplay -- --check) exited 1 for an existing extra blank line in crates/deadsync-gameplay/tests/held_lane_performance.rs. Its before/current Git blob is 1f69fd696cce345682dc4c727cf3c94eb809f4bd, and the recorded working tree was clean. The standalone rustfmt check of the five include! fragments also exited 1 with compact formatting differences. Cargo fmt does not traverse these include! fragments. Both checks were read only, and neither is a passing formatting gate. These formatting results are separate from the parity comparison outcomes above. Retained standalone output may be truncated; the receipt records that limitation. No formatting command was rerun to create this report.

## Resource use and cleanup

| Chart | Phase | Unit memory peak (bytes) | CPU (ns) | Memory limit (bytes) | Swap limit (bytes) | CPU quota / second | Unit result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Nishi-Shinjuku seisou kyoku | native capture and archive | 2104893440 | 151320006000 | 6442450944 | 0 | 2s | success |
| Circles (native title Episode 15) | native capture and archive | 1196322816 | 349067492000 | 6442450944 | 0 | 2s | success |
| [CRYSTAL_ACCESS] | native capture; wrapper validation failed | 1599619072 | 182301458000 | 6442450944 | 0 | 2s | exit-code |
| [CRYSTAL_ACCESS] | archive recovery; no native recapture | 1647484928 | 19747864000 | 6442450944 | 0 | 2s | success |
| And Drugs | native capture and archive | 2620530688 | 194425500000 | 6442450944 | 0 | 2s | success |
| Flying Castle | native capture and archive | 2809458688 | 193005814000 | 6442450944 | 0 | 2s | success |

Maximum memory peak across each chart's capture and any recovery stages:

| Chart | Maximum unit peak (bytes) | Sum of phase CPU (ns) |
| --- | --- | --- |
| Nishi-Shinjuku seisou kyoku | 2104893440 | 151320006000 |
| Circles (native title Episode 15) | 1196322816 | 349067492000 |
| [CRYSTAL_ACCESS] | 1647484928 | 202049322000 |
| And Drugs | 2620530688 | 194425500000 |
| Flying Castle | 2809458688 | 193005814000 |

[CRYSTAL_ACCESS]: native capture completed, but the local wrapper rejected the legitimate empty drawable sample list. The corrected validator allows zero submitted draw samples while requiring captured drawable frames, native drawable vertices support, and zero capture drops. The existing native trace was validated and archived; native capture was not rerun. The original failed receipt remains preserved. The capture and recovery phase resource receipts above are separate, and the maximum includes both.


Unit peaks include capture and archive work. Captures are serialized under the retained plan's 200% CPU and 6 GiB memory limit with swap disabled.

Confirmed obsolete guest intermediates: 5,815 files deleted, 10,411,036,590 logical bytes and 10,423,693,312 allocated bytes; 126 retained files unchanged. Guest free space rose from 36,098,609,152 to 46,521,077,760 bytes (gain 10,422,468,608). This is the guest filesystem delta, not a host-wide reclamation claim.

6 completed orchestration attempt receipts are preserved in coverage.json, including failed attempts before successful final downloads.

## Exact remaining coverage

The following strings are copied from final reports. Pending coverage is distinct from an implemented comparison failure. Combined lists and baseline/original-reference lists are retained verbatim in coverage.json.

### Nishi-Shinjuku seisou kyoku

Diagnostic/report pending coverage:

- uncompared song operations: Actor.GetX, Actor.GetY, Actor.GetZ, Actor.SetTextureFiltering, Actor.basezoom, Actor.basezoomx, Actor.basezoomy, Actor.blend, Actor.effectclock, Actor.fadebottom, Actor.hibernate, Actor.rotationx, Actor.rotationy, Actor.skewx, Actor.wag, Actor.z, Actor.zoomz, GameState.IsHumanPlayer, PlayerOptions.FromString, PlayerOptions.Mini, PlayerOptions.Tilt
- native drawable state/resources: Quad, Sprite
- missing captured subscriber identity for ScreenGameplay/2/11/1
- missing captured subscriber identity for ScreenGameplay/2/12
- missing captured subscriber identity for ScreenGameplay/2/15/1
- missing captured subscriber identity for ScreenGameplay/2/5/2/1
- missing captured subscriber identity for ScreenGameplay/2/5/2/2
- missing captured subscriber identity for ScreenGameplay/2/5/2/3
- missing captured subscriber identity for ScreenGameplay/2/5/2/4
- missing captured subscriber identity for ScreenGameplay/2/5/2/5
- missing captured subscriber identity for ScreenGameplay/2/5/2/6
- missing captured subscriber identity for ScreenGameplay/2/5/3/1
- missing captured subscriber identity for ScreenGameplay/2/5/3/2
- missing captured subscriber identity for ScreenGameplay/2/5/3/3
- missing captured subscriber identity for ScreenGameplay/2/5/3/4
- missing captured subscriber identity for ScreenGameplay/2/5/3/5
- missing captured subscriber identity for ScreenGameplay/2/5/3/6
- missing captured subscriber identity for ScreenGameplay/2/8
- missing captured subscriber identity for ScreenGameplay/25
- missing captured subscriber identity for ScreenGameplay/26/1/1
- missing captured subscriber identity for ScreenGameplay/26/1/10
- missing captured subscriber identity for ScreenGameplay/26/1/12
- missing captured subscriber identity for ScreenGameplay/26/1/2
- missing captured subscriber identity for ScreenGameplay/26/1/4
- missing captured subscriber identity for ScreenGameplay/26/1/5
- missing captured subscriber identity for ScreenGameplay/26/1/7
- missing captured subscriber identity for ScreenGameplay/26/1/9
- missing captured subscriber identity for ScreenGameplay/3/1

Nested production pending coverage:

- application build without test-support
- full-song completion
- sampled framebuffer pixels
- production command/query instrumentation
- complete stage finalization, aggregate/evaluation history and public STATSMAN:Reset
- saved statistics getter functions explicitly invoked with another stage's player receiver
- BitmapText submitted glyph geometry, texture bindings and RGBA (live text content is compared)

### Circles (native title Episode 15)

Diagnostic/report pending coverage:

- native drawable state/resources: ActorProxy, Quad, Sprite
- missing captured subscriber identity for ScreenGameplay/2/11/1
- missing captured subscriber identity for ScreenGameplay/2/12
- missing captured subscriber identity for ScreenGameplay/2/15/1
- missing captured subscriber identity for ScreenGameplay/2/5/2/1
- missing captured subscriber identity for ScreenGameplay/2/5/2/2
- missing captured subscriber identity for ScreenGameplay/2/5/2/3
- missing captured subscriber identity for ScreenGameplay/2/5/2/4
- missing captured subscriber identity for ScreenGameplay/2/5/2/5
- missing captured subscriber identity for ScreenGameplay/2/5/2/6
- missing captured subscriber identity for ScreenGameplay/2/5/3/1
- missing captured subscriber identity for ScreenGameplay/2/5/3/2
- missing captured subscriber identity for ScreenGameplay/2/5/3/3
- missing captured subscriber identity for ScreenGameplay/2/5/3/4
- missing captured subscriber identity for ScreenGameplay/2/5/3/5
- missing captured subscriber identity for ScreenGameplay/2/5/3/6
- missing captured subscriber identity for ScreenGameplay/2/8
- missing captured subscriber identity for ScreenGameplay/25
- missing captured subscriber identity for ScreenGameplay/26/1/1
- missing captured subscriber identity for ScreenGameplay/26/1/10
- missing captured subscriber identity for ScreenGameplay/26/1/12
- missing captured subscriber identity for ScreenGameplay/26/1/2
- missing captured subscriber identity for ScreenGameplay/26/1/4
- missing captured subscriber identity for ScreenGameplay/26/1/5
- missing captured subscriber identity for ScreenGameplay/26/1/7
- missing captured subscriber identity for ScreenGameplay/26/1/9
- missing captured subscriber identity for ScreenGameplay/3/1

Nested production pending coverage:

- application build without test-support
- full-song completion
- sampled framebuffer pixels
- production command/query instrumentation
- complete stage finalization, aggregate/evaluation history and public STATSMAN:Reset
- saved statistics getter functions explicitly invoked with another stage's player receiver
- BitmapText submitted glyph geometry, texture bindings and RGBA (live text content is compared)

### [CRYSTAL_ACCESS]

Diagnostic/report pending coverage:

- uncompared song operations: Actor.bob, Actor.effectoffset, Actor.skewx, PlayerOptions.Alternate, PlayerOptions.Brake, PlayerOptions.Confusion, PlayerOptions.Cross, PlayerOptions.Dark, PlayerOptions.Drunk, PlayerOptions.Flip, PlayerOptions.Invert, PlayerOptions.Split, PlayerOptions.Stealth, PlayerOptions.Tipsy, PlayerOptions.Tornado
- missing captured subscriber identity for ScreenGameplay/2/11/1
- missing captured subscriber identity for ScreenGameplay/2/12
- missing captured subscriber identity for ScreenGameplay/2/15/1
- missing captured subscriber identity for ScreenGameplay/2/5/2/1
- missing captured subscriber identity for ScreenGameplay/2/5/2/2
- missing captured subscriber identity for ScreenGameplay/2/5/2/3
- missing captured subscriber identity for ScreenGameplay/2/5/2/4
- missing captured subscriber identity for ScreenGameplay/2/5/2/5
- missing captured subscriber identity for ScreenGameplay/2/5/2/6
- missing captured subscriber identity for ScreenGameplay/2/5/3/1
- missing captured subscriber identity for ScreenGameplay/2/5/3/2
- missing captured subscriber identity for ScreenGameplay/2/5/3/3
- missing captured subscriber identity for ScreenGameplay/2/5/3/4
- missing captured subscriber identity for ScreenGameplay/2/5/3/5
- missing captured subscriber identity for ScreenGameplay/2/5/3/6
- missing captured subscriber identity for ScreenGameplay/2/8
- missing captured subscriber identity for ScreenGameplay/25
- missing captured subscriber identity for ScreenGameplay/26/1/1
- missing captured subscriber identity for ScreenGameplay/26/1/10
- missing captured subscriber identity for ScreenGameplay/26/1/12
- missing captured subscriber identity for ScreenGameplay/26/1/2
- missing captured subscriber identity for ScreenGameplay/26/1/4
- missing captured subscriber identity for ScreenGameplay/26/1/5
- missing captured subscriber identity for ScreenGameplay/26/1/7
- missing captured subscriber identity for ScreenGameplay/26/1/9
- missing captured subscriber identity for ScreenGameplay/3/1

Nested production pending coverage:

- application build without test-support
- full-song completion
- sampled framebuffer pixels
- production command/query instrumentation
- complete stage finalization, aggregate/evaluation history and public STATSMAN:Reset
- saved statistics getter functions explicitly invoked with another stage's player receiver
- BitmapText submitted glyph geometry, texture bindings and RGBA (live text content is compared)
- native capture contains no drawable samples; drawable comparison was not exercised

### And Drugs

Diagnostic/report pending coverage:

- uncompared song operations: Actor.rotationx, Actor.zoomy, Actor.zoomz, PlayerOptions.Alternate, PlayerOptions.Beat, PlayerOptions.Brake, PlayerOptions.Cross, PlayerOptions.Dark, PlayerOptions.Dizzy, PlayerOptions.Drunk, PlayerOptions.Flip, PlayerOptions.Invert, PlayerOptions.Split, PlayerOptions.Stealth, PlayerOptions.Sudden, PlayerOptions.SuddenOffset, PlayerOptions.Tipsy
- missing captured subscriber identity for ScreenGameplay/2/11/1
- missing captured subscriber identity for ScreenGameplay/2/12
- missing captured subscriber identity for ScreenGameplay/2/15/1
- missing captured subscriber identity for ScreenGameplay/2/5/2/1
- missing captured subscriber identity for ScreenGameplay/2/5/2/2
- missing captured subscriber identity for ScreenGameplay/2/5/2/3
- missing captured subscriber identity for ScreenGameplay/2/5/2/4
- missing captured subscriber identity for ScreenGameplay/2/5/2/5
- missing captured subscriber identity for ScreenGameplay/2/5/2/6
- missing captured subscriber identity for ScreenGameplay/2/5/3/1
- missing captured subscriber identity for ScreenGameplay/2/5/3/2
- missing captured subscriber identity for ScreenGameplay/2/5/3/3
- missing captured subscriber identity for ScreenGameplay/2/5/3/4
- missing captured subscriber identity for ScreenGameplay/2/5/3/5
- missing captured subscriber identity for ScreenGameplay/2/5/3/6
- missing captured subscriber identity for ScreenGameplay/2/8
- missing captured subscriber identity for ScreenGameplay/25
- missing captured subscriber identity for ScreenGameplay/26/1/1
- missing captured subscriber identity for ScreenGameplay/26/1/10
- missing captured subscriber identity for ScreenGameplay/26/1/12
- missing captured subscriber identity for ScreenGameplay/26/1/2
- missing captured subscriber identity for ScreenGameplay/26/1/4
- missing captured subscriber identity for ScreenGameplay/26/1/5
- missing captured subscriber identity for ScreenGameplay/26/1/7
- missing captured subscriber identity for ScreenGameplay/26/1/9
- missing captured subscriber identity for ScreenGameplay/3/1

Nested production pending coverage:

- application build without test-support
- full-song completion
- sampled framebuffer pixels
- production command/query instrumentation
- complete stage finalization, aggregate/evaluation history and public STATSMAN:Reset
- saved statistics getter functions explicitly invoked with another stage's player receiver
- BitmapText submitted glyph geometry, texture bindings and RGBA (live text content is compared)
- native capture contains no drawable samples; drawable comparison was not exercised

### Flying Castle

Diagnostic/report pending coverage:

- uncompared song operations: Actor.z, Actor.zoomy, Actor.zoomz, PlayerOptions.Beat, PlayerOptions.Brake, PlayerOptions.Bumpy, PlayerOptions.Centered, PlayerOptions.ConfusionOffset1, PlayerOptions.ConfusionOffset2, PlayerOptions.ConfusionOffset3, PlayerOptions.ConfusionOffset4, PlayerOptions.Dark, PlayerOptions.Dizzy, PlayerOptions.Drunk, PlayerOptions.DrunkOffset, PlayerOptions.Flip, PlayerOptions.Invert, PlayerOptions.MoveX1, PlayerOptions.MoveX2, PlayerOptions.MoveX3, PlayerOptions.MoveX4, PlayerOptions.MoveY1, PlayerOptions.MoveY2, PlayerOptions.MoveY3, PlayerOptions.MoveY4, PlayerOptions.Stealth, PlayerOptions.Tiny, PlayerOptions.Tipsy, PlayerOptions.Tornado
- missing captured subscriber identity for ScreenGameplay/2/11/1
- missing captured subscriber identity for ScreenGameplay/2/12
- missing captured subscriber identity for ScreenGameplay/2/15/1
- missing captured subscriber identity for ScreenGameplay/2/5/2/1
- missing captured subscriber identity for ScreenGameplay/2/5/2/2
- missing captured subscriber identity for ScreenGameplay/2/5/2/3
- missing captured subscriber identity for ScreenGameplay/2/5/2/4
- missing captured subscriber identity for ScreenGameplay/2/5/2/5
- missing captured subscriber identity for ScreenGameplay/2/5/2/6
- missing captured subscriber identity for ScreenGameplay/2/5/3/1
- missing captured subscriber identity for ScreenGameplay/2/5/3/2
- missing captured subscriber identity for ScreenGameplay/2/5/3/3
- missing captured subscriber identity for ScreenGameplay/2/5/3/4
- missing captured subscriber identity for ScreenGameplay/2/5/3/5
- missing captured subscriber identity for ScreenGameplay/2/5/3/6
- missing captured subscriber identity for ScreenGameplay/2/8
- missing captured subscriber identity for ScreenGameplay/25
- missing captured subscriber identity for ScreenGameplay/26/1/1
- missing captured subscriber identity for ScreenGameplay/26/1/10
- missing captured subscriber identity for ScreenGameplay/26/1/12
- missing captured subscriber identity for ScreenGameplay/26/1/2
- missing captured subscriber identity for ScreenGameplay/26/1/4
- missing captured subscriber identity for ScreenGameplay/26/1/5
- missing captured subscriber identity for ScreenGameplay/26/1/7
- missing captured subscriber identity for ScreenGameplay/26/1/9
- missing captured subscriber identity for ScreenGameplay/3/1

Nested production pending coverage:

- application build without test-support
- full-song completion
- sampled framebuffer pixels
- production command/query instrumentation
- complete stage finalization, aggregate/evaluation history and public STATSMAN:Reset
- saved statistics getter functions explicitly invoked with another stage's player receiver
- BitmapText submitted glyph geometry, texture bindings and RGBA (live text content is compared)
- native capture contains no drawable samples; drawable comparison was not exercised

## Provenance

- Native oracle identity: {"harness_commit": ["b2af4f355d827fb0e89aead84b4c75a9b8cccf6c"], "harness_sha256": ["1780c9e517994285775fa75c98c1975c601be0f94c4ad1a376cab16bd8684e8e"], "native_revision": ["663525dcb86eb570d0ef6a2e209678436660ae26"]}.
- Selection SHA256: b1e4edf40dfe2c2fe8095d0265bd400b3758866f4cf59edc5bac700d85d9e6bb.
- Failure ledger: C:\GitHub\deadsync-tests\full_song_lua\proxmox-followup-2026-11-20\fleet-accounting\accounting.json.gz; SHA256 2a9972a9f6d71644bdd80c8a1201b5f18851cb2809ffd18ffeb6417949237802.
- Final replay binary SHA256: 8fe05b17d1edc96cf705e7f68477d7c96fce0b5720367d04b7e1c22533e7f06b.
- Summarizer SHA256: e8d708696d043f3808cf1a54302717b17b0a0cbfaaab7d74de412ea9bf90842b.
- Exact report, execution, archive, native evidence, build and source hashes are in coverage.json.

Runtime fix commit: cfc285847c362a079faefc9840dc488223b87ca8. Its five gameplay files match the final replay and focused regression source hashes.
