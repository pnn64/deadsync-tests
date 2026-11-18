# Paperclip live statistics and failure control

This bounded native capture exercises the original song with human input in versus mode. It supplements the accepted full-song autoplay fixture, which cannot exercise changing judgments, score, or life. It is not a full-song replacement or pixel comparison.

The native harness completed successfully: 1,455 update frames, 19,854 semantic events, 8,826 drawable samples, all 146 input commands observed, zero script errors, zero transition errors, and no dropped records. Requested pacing was 60 FPS; actual capture clocks are retained in the trace. P1 hits eight taps through beat 58, P2 hits 65 through beat 98, then both stop. FailOff keeps gameplay active for the authored failure poll.

`manifest.json` pins the exact compressed trace, input pulses, all 23 original song files, and the accepted source archive. `source-provenance.json` pins the engine, harness, installed theme, options, and source hashes. `pulse-capture-command.json` is the actual successful capture invocation. `pulse-capture-summary.json` records its validation. `observations-summary.json` is derived from this trace. Source files were unchanged before and after capture.

| Music seconds | Native observation |
| --- | --- |
| 16.903446197509766 | Both score displays first show `00.09`. |
| 19.244285583496094 | P1 peaks at life 0.564000129699707 and displayed score `00.81`. |
| 21.532108306884766 | P1 meter first observes zero; Word remains visible while P2 continues. |
| 32.298912048339844 | P2 reaches life 1, eighteen meter glyphs, and rainbow. |
| 32.39160919189453 | P2 score peaks at `06.45`. |
| 34.37854766845703 | Update 1186 submits the final Word descendant draw. |
| 34.40702819824219 | Both life queries return zero; one authored Failed broadcast; first BSOD draw on update 1187. |

Zero timestamps are first authored polls, not unsampled physical crossing times. Native GetFailed stays false under FailOff; Paperclip checks life directly. The unchanged song polls its meters every 0.1 seconds and failure every 0.5 seconds. Versus requires both players at zero. In solo, the script chooses P1 if enabled, otherwise P2, and uses the actor names `1P meter` / `1P score` for either solo player. This native capture is versus only.

The rebuilt production Runtime replay passed: all 1,455 frames, 146 inputs, 46 stage samples / 1,012 stage fields, 8,826 drawable samples / 31,962 vertices / 3,492 text samples matched, with zero mismatches and errors. Source identity is verified against all 560 archived song/support files. `final-production-report.json` contains the complete report; `final-production-command.json` pins the rebuilt executable, invocation, timing, and unchanged source checks. Seven degenerate culls were equivalent, and no owned immediate draws were left uncompared.

No preliminary or rejected run is included in this evidence folder. `archive_accepted`, `whole_song_parity_proven`, and `pixel_parity_proven` remain false for this bounded control. The final report retains these pending coverage items verbatim:

- application build without test-support (run song_lua_execution)
- full-song completion
- sampled framebuffer pixels
- production command/query instrumentation

From the DeadSync checkout, replay the retained trace against the unchanged original song:

```powershell
cargo test --test live_song_lua -- 'tests/fixtures/interactive_song_lua/paperclip-live-stats-2026-11-18/native-human-pulses.json.zst' 'C:/GitHub/deadsync/save/paperclip-live-stats-2026-11-18/replay-source/Paperclip/Paperclip.ssc' 'save/paperclip-live-stats-2026-11-18/final-production-report.json' --production
```

The existing runner reads zstd directly and verifies the trace, source archive, and every archived `song/` file using the adjacent manifest. The replay source above is the accepted archive's `song/` tree extracted into an isolated directory: it contains the original 23 song files plus archived `__songlua_theme_path` support assets. On another machine, extract that complete tree to a directory named Paperclip and supply its Paperclip.ssc path; an ordinary installation alone lacks the archived support files required by this source verifier. Run `python scripts/prepare_test_fixtures.py` first if the source archive has not been restored from its committed parts. The production replay explicitly prepares Runtime Lua; the separate shell regression verifies Baked selection falls back to Runtime for live statistics.
