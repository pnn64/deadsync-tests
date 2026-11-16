# Heavy song Lua CPU profiles

Baseline collection on Proxmox: two vCPUs, 64 GiB guest RAM, 58 GiB process limit, samply 0.13.1 at 99 Hz. Each profile covers a complete replay with archive validation and report generation. Archive decompression happened before recording. OS caches were not cleared; these are repeated runs, not controlled cold/warm benchmarks.

The release runner retains debug information and frame pointers, with LTO disabled and 16 codegen units. See [build provenance](build-proof.json) for the exact baseline source, preserved worktree edits and executable hash. These are baseline profiles collected concurrently with correctness work, not profiles of subsequent fixes.

| Fixture | Run | Replay + profiler seconds | CPU samples | Replay passed | Unresolved leaf samples |
| --- | --- | ---: | ---: | --- | ---: |
| mr sandman/mr sandman.sm | 1 | 802.554 | 78864 | True | 10 |
| mr sandman/mr sandman.sm | 2 | 809.226 | 79514 | True | 13 |
| Paint the Town Red/PaintTheTownRed.ssc | 1 | 379.737 | 36903 | True | 14 |
| Paint the Town Red/PaintTheTownRed.ssc | 2 | 380.873 | 37179 | True | 14 |

Percentages below are shares of sampled CPU stacks, not wall-clock shares. Exclusive samples identify the currently executing physical function; inclusive samples include descendants and overlap. Full inclusive/exclusive top-30 tables are in each hotspots.json. Portable .syms.json files accompany every saved profile.

## mr sandman/mr sandman.sm — run 1

[Profile](mr-sandman/run-1/profile.json.gz) · [Symbols](mr-sandman/run-1/profile.json.syms.json) · [Hotspot data](mr-sandman/run-1/hotspots.json) · [Run provenance](mr-sandman/run-1/result.json)

| Exclusive CPU samples | Function |
| ---: | --- |
| 9.62% | `<deadlib_lua::vm::Vm>::run` |
| 7.94% | `deadsync_song_lua::actors::initial_state::read_fields` |
| 7.74% | `_memmove_sse2_unaligned_erms` |
| 5.10% | `<indexmap::map::IndexMap<alloc::string::String, serde_json::value::Value>>::get_index_of::<str>` |
| 5.08% | `<deadlib_lua::table::Table>::get_key` |
| 4.53% | `<deadlib_lua::vm::host::HostCall>::raw_table_get_static` |
| 3.94% | `<deadlib_lua::vm::Vm>::is_live_value` |
| 3.71% | `int_malloc` |
| 3.08% | `_GI___libc_malloc` |
| 2.85% | `deadsync_song_lua::actors::effects::advance` |
| 2.69% | `sha2::sha256::soft::unroll::compress` |
| 2.15% | `<deadsync_song_lua::actors::fields::Reader>::new` |

## mr sandman/mr sandman.sm — run 2

[Profile](mr-sandman/run-2/profile.json.gz) · [Symbols](mr-sandman/run-2/profile.json.syms.json) · [Hotspot data](mr-sandman/run-2/hotspots.json) · [Run provenance](mr-sandman/run-2/result.json)

| Exclusive CPU samples | Function |
| ---: | --- |
| 9.49% | `<deadlib_lua::vm::Vm>::run` |
| 7.66% | `_memmove_sse2_unaligned_erms` |
| 7.54% | `deadsync_song_lua::actors::initial_state::read_fields` |
| 6.06% | `<indexmap::map::IndexMap<alloc::string::String, serde_json::value::Value>>::get_index_of::<str>` |
| 4.86% | `<deadlib_lua::table::Table>::get_key` |
| 4.22% | `<deadlib_lua::vm::host::HostCall>::raw_table_get_static` |
| 3.94% | `int_malloc` |
| 3.90% | `<deadlib_lua::vm::Vm>::is_live_value` |
| 2.83% | `sha2::sha256::soft::unroll::compress` |
| 2.81% | `_GI___libc_malloc` |
| 2.77% | `deadsync_song_lua::actors::effects::advance` |
| 2.17% | `<deadsync_song_lua::actors::fields::Reader>::new` |

## Paint the Town Red/PaintTheTownRed.ssc — run 1

[Profile](paint-ssc/run-1/profile.json.gz) · [Symbols](paint-ssc/run-1/profile.json.syms.json) · [Hotspot data](paint-ssc/run-1/hotspots.json) · [Run provenance](paint-ssc/run-1/result.json)

| Exclusive CPU samples | Function |
| ---: | --- |
| 16.94% | `sha2::sha256::soft::unroll::compress` |
| 11.76% | `int_malloc` |
| 7.42% | `_GI___libc_malloc` |
| 4.70% | `int_free` |
| 3.97% | `<alloc::vec::Vec<deadsync_song_lua::SongLuaHostClockInput> as core::clone::Clone>::clone` |
| 3.95% | `<indexmap::map::IndexMap<alloc::string::String, serde_json::value::Value>>::get_index_of::<str>` |
| 3.75% | `malloc_consolidate` |
| 3.20% | `_memcmp_sse2` |
| 2.73% | `<indexmap::map::IndexMap<alloc::string::String, serde_json::value::Value>>::get_mut::<alloc::string::String>` |
| 2.26% | `unlink_chunk.isra.0` |
| 1.96% | `_memmove_sse2_unaligned_erms` |
| 1.81% | `<deadlib_lua::table::Table>::get_key` |

## Paint the Town Red/PaintTheTownRed.ssc — run 2

[Profile](paint-ssc/run-2/profile.json.gz) · [Symbols](paint-ssc/run-2/profile.json.syms.json) · [Hotspot data](paint-ssc/run-2/hotspots.json) · [Run provenance](paint-ssc/run-2/result.json)

| Exclusive CPU samples | Function |
| ---: | --- |
| 17.03% | `sha2::sha256::soft::unroll::compress` |
| 12.28% | `int_malloc` |
| 6.86% | `_GI___libc_malloc` |
| 4.53% | `int_free` |
| 4.12% | `<alloc::vec::Vec<deadsync_song_lua::SongLuaHostClockInput> as core::clone::Clone>::clone` |
| 3.95% | `<indexmap::map::IndexMap<alloc::string::String, serde_json::value::Value>>::get_index_of::<str>` |
| 3.63% | `malloc_consolidate` |
| 3.30% | `_memcmp_sse2` |
| 2.84% | `<indexmap::map::IndexMap<alloc::string::String, serde_json::value::Value>>::get_mut::<alloc::string::String>` |
| 2.29% | `unlink_chunk.isra.0` |
| 1.97% | `<deadlib_lua::table::Table>::get_key` |
| 1.86% | `_memmove_sse2_unaligned_erms` |
