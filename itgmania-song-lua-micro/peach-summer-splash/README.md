# Peach Summer Splash native references

Both captures were recorded with itgmania-harness 0.1.111 and native ITGmania OpenGL with a hidden 854×480 window, Single
Challenge, 2× Cel, autoplay, native variable updates, and a 60 Hz capture
target. [The manifest](manifest.json) pins the input bytes, executable and
observer hashes, exact capture arguments, and the recorded clocks.

- `sandbox-offset-native.json.zst` captures beats 30.5–37. It includes the
  beat-34 tap wrapping toward the receptor, the beat-36 tap across the Offset
  reset at 35.875, and the second column's hold from 31.25 to 32 across the
  bend at 31.875. The trace retains native Model anchors, hold-strip vertices,
  and receptor visits, including the transparent receptors.
- `original-aft-native.json.zst` captures the original chart's startup.
  The `ScreenTex` and `BlurTex` calls from `OnCommand` have distinct native
  passes during the update. The first regular draw then records
  `ScreenTex` → `BlurTex` → screen. The boundary cursor and the active target
  identify the submissions within each pass. These observations cover
  geometry and render-target order.

Run `song-lua-trace` from this directory with the arguments in the manifest.
Use a trace executable built with `native/trace_adapter.cmake` and the
`Harness Simply Love` theme installed beside the pinned engine. The original
uses the semantic drawable profile with `--render-target-passes`. The
sandbox uses `--notefield-samples`. Captures use native wall-clock pacing, so
fresh runs can submit the same note at slightly different beats. The archived
clocks define the reference inputs for a Deadsync replay.
