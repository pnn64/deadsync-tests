# Current source supplement: af6a6c9e

Selected source commit: `af6a6c9e045f5dfb13abe38bd4eb58d7326f2e26` on `main`. The working tree was clean when this supplement was captured. Every source file recorded by the after07 regression execution matches the committed file bytes. The build ran before the source commit was created; the matching hashes, rather than a rewritten build identity, bind these results to the selected commit.

The after07 regression evidence is green: **301 focused tests plus 26 interactive comparator tests = 327 passed, 0 failed, 3 ignored**. Full playback accounts for 256 passed and all three ignored tests. No tests were launched while preparing this supplement.

## Final selected-wrapper-x encoding regression

`attempted_call_encoding_errors_remain_diagnostic_failures` now passes using the selected `wrapper.x` forward after that wrapper is removed (`native_gameplay.rs:3844-3913`). A baseline `pcall(selected, wrapper, 0, 0)` establishes the receiver-lifetime error. A second call adds a malformed cyclic actor-tag table as an unused extra argument. The binding still produces exactly the baseline Lua error; the observer retains exactly one genuine encoding diagnostic. Assertions also preserve raw Lua fields, reject invented return/tween metadata on failed calls, and verify a later successful `aux(74)` observation.

This final regression supersedes the historical intermediate RemoveWrapperState-extra-argument proposal. It tests observable attempted calls, error preservation, and observer cleanup. The first x argument is numeric and the receiver is already removed, so it does **not** establish argument validation for `x(table)` on a valid actor.

## Two source gaps remain unchanged

- **Production Underlay child glow:** normal native ActorFrame children inherit final glow independently of diffuse (`ActorFrame.cpp:251-274`, `Actor.cpp:641-664`). The production Underlay source producer still applies layer diffuse only (`playback.rs:16185,16201,16217,16273,16294`; helper `7628-7648`). The passing external-source regression covers entry admission and basis preservation using synthetic shared children; it does not prove production Underlay child-glow propagation.
- **Valid Actor.x table-argument errors:** native `Actor.cpp:1685-1688` uses `FArg`, defined as `luaL_checknumber` (`LuaManager.h:271`; bundled `lauxlib.c:184-188`), which rejects a table. Owned scalar handling still returns success when conversion fails (`actors.rs:2955-2965,3097-3109`; bound return at `actors/scalar_methods.rs:475-491`). The selected-wrapper-x regression does not change or cover that separate valid-receiver contract.

The JSON supplement verifies these runtime/native source hashes are unchanged from the retained gap report and records committed blob identities for the owned sources. Earlier reports and correction proofs remain unchanged as historical evidence. Use the coordinator's **final checkpoint summary** for final native replay outcomes and acceptance coverage; this supplement does not publish another native-case status table.

## Exact ignored tests

| Test | Declared reason |
|---|---|
| `playback::actor_conformance::movie_metadata_tests::movie_source_dimensions_preserve_fullscreen_and_cropped_geometry` | requires ffprobe on PATH or in the runtime bin directory |
| `playback::tests::manual_player_draws_keep_recorded_pixels` | requires a local Vulkan device and window |
| `playback::tests::song_lua_preloaded_aft_chain_preserves_pixels` | requires a Vulkan device and a window system |

Names and reasons match both the after07 log and current source attributes. The JSON receipt pins the committed source hashes, completed regression logs/receipts, native anchors, historical reports, and this supplement. Only new ignored evidence files were written.
