# Eros and Apollo native reference

`inputs/` preserves the original `eros.sm` and its assets. The chart schedules
one XML background and twenty XML foreground instances. The game mode is dance
single, Challenge, Puuro, with P1 autoplay and `2x, cel`.

`native-off.json.zst` covers startup with `QuirksMode=0`. Native foreground
loading still creates entries for the schedule. The playfield takes the dummy
actor path and finishes on the first eligible frame without executing the
embedded modifier commands.

`native-on.json.zst` covers the complete game with `QuirksMode=1`. The pinned
ITGmania executable reaches gameplay exit and commits one stage. The trace
retains twenty load and activation records, nineteen finishes, and 654 calls
to `GameState:ApplyGameCommand`. The playfield stays active through the song.
Repeated foreground names identify separate native instances. The fallback
theme logs `hidden()` deprecations and still applies those calls.

The legacy `.model` filenames in `chart` and `chart2` resolve to files, then
the pinned `ActorUtil::MakeActor` uses dummy actors for their unknown type.
The OpenGL captures retain scene submissions in these windows.

| Trace | Beats | Evidence |
|---|---:|---|
| `native-intro-geometry` | 14–20 | First hold and playfield state |
| `native-sprite-geometry` | 95–100 | The first `girls` animation and sprite UVs |
| `native-model-geometry` | 158–165 | Domino `.txt` model submissions |
| `native-movie-geometry` | 174–196 | `how/lights.mpg` and both `turn/dix.mpg` actors |
| `native-chart-geometry` | 366–374 | `chart2` activation and the scene that actually draws |

The manifest records SHA-256 hashes of the original inputs, compressed and
uncompressed traces, and native observer. Run `song-lua-trace` with the pinned
native executable and the arguments in the manifest to refresh a trace.
