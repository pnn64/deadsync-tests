# Native typed render-target UV control

Captured on 2026-11-20 with `itgmania-harness` commit
`b2af4f355d827fb0e89aead84b4c75a9b8cccf6c` (version 0.1.110), native ITGmania
`663525dcb86eb570d0ef6a2e209678436660ae26`, and Simply Love
`1feda1fd43d96baca951351bb28a35d5e690ebc7`.

The foreground creates one 854x480 ActorFrameTexture, obtains its native
`RageTextureRenderTarget`, and binds that object to an ActorMultiVertex. A manual
draw callback submits the same quad strip after drawing the render target. Native
OpenGL allocates a 1024x512 backing texture and preserves the authored maximum UV
coordinates `(0.833984375, 0.9375)` in every mesh submission. Converting these
coordinates to image-relative `(1, 1)` changes the observed native values.

The complete capture contains 537 native update frames, 473 events, 450 drawable
samples, and 18 stage samples. The mesh contributes 225 samples and 225 explicit
`Actor.Draw` calls after exactly one typed texture binding. Its target fill
contributes the other 225 samples. Native gameplay exited to evaluation with the
stage committed, with no script errors or dropped observations. These figures
describe native capture coverage; replay acceptance is recorded separately.

The typed binding is event 19 and the first mesh draw is event 25. Both report
the identical native song clock, `0.11022675782442093` seconds; that draw pairs
with update 228. Event 27 pairs with update 229 at `0.23342403769493103` seconds.
All 225 ordered draw calls pair with one sample at the exact corresponding frame
clock. This capture therefore requires binding causality to follow event order;
a requirement for the song clock to strictly increase would reject native input.

`native-capture-evidence.zip` contains the unchanged native trace, source inputs,
binary and build proofs, capture/archive commands, and systemd completion
receipts. The capture used at most two CPUs and a 6 GiB memory limit with swap
disabled. Recorded peak memory was 273,666,048 bytes for capture and 142,708,736
bytes for archive creation. `observation-proof.json` records the exact native
binding, dimensions, UV values, and candidate archive hash.

The first control had no tween duration and produced zero drawable samples.
`Foreground::Update` in the pinned native source computes a foreground's stop beat
from its tween duration after `OnCommand`; the zero-duration root was hidden
before drawing. The second control adds an authored six-second sleep. Compact
metadata and this source difference are retained in
`attempt01-inadequate-coverage.json`; its raw trace and candidate remain outside
the committed fixture evidence. The first attempt is not accepted coverage.

The retained historical pass4 runner (SHA-256
`90abd15f5e2f6e15a23b33faacc83ec81bde13a2f709f095576a10ce0c8405e4`)
was also run with `--production`, under the same two-CPU and 6 GiB limits and a
180-second deadline. It exited 1 before writing a replay report because its draw
comparator does not support the native `QuadStrip` primitive. Its source/build
proofs, exact command, log, and completion receipt are retained in
`historical-baseline-evidence.zip`, summarized by `historical-baseline.json`.
This result does not measure the UV mismatch or establish current-main acceptance.

The uncompressed candidate
`11064b28f2572ca8a90e532e1639f30b416794ae886e7adf7e286c0c91324ac0.tar`
passed combined diagnostic and production gameplay replay with exit 0. The
runner binary SHA-256 is
`db462d6906c1c904b7a786483e0719d09cc7fb120d73a9bf0df12ed3da7a1e25`;
its compiled comparator source is bound to DeadSync commit
`a29b55646dd492dc8503335be72b91488fb82290` in the retained source receipt.
Both paths replayed all 537 frames and compared 450 draws, 2,700 vertices, and
225 typed AFT samples, with zero mismatches or errors. The diagnostic path
compared 2,038 stage fields and the two paths together compared 4,076.

`current-main-replay-evidence.zip` retains the exact report, invocation, execution
receipt, logs, compiled comparator source, and source binding. The report's
SHA-256 is `5431ce026d06f1a8dabfdd31f4dc2fb829c90452043ef1a52767992c51cc5ad5`.
`replay-summary.json` records the gates, counts, and all 35 pending coverage
entries. The control captures no input events, so its broader interactive gate
is false despite passing both drawable comparison paths. The whole-song,
production-parity, and framebuffer-pixel proof flags remain false.

The latest verified harness packed that exact accepted candidate and report as
`bc906861bee61bfd9cb364c6cafe9dff54e9c852a7c477ffa8a9ef785fbd3c0d.tar.zst`
(107,774,338 bytes; SHA-256 is the filename stem). `pack-evidence.zip` retains the
exact command, result, log, and completion receipt. Packing used at most two
CPUs and 6 GiB with swap disabled; peak memory was 330,817,536 bytes.
