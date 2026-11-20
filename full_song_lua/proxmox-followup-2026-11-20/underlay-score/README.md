# Native gameplay score snapshot correction

The existing native Simply Love score script initializes each score actor at its
player-specific position, with zoom `0.5` and text `0.00`. The underlay snapshot
still contained the earlier placeholder at `(0, 0)`, zoom `1`, and `0.00%`.

Fixture commit `e827751b995cfdb37edd4abe6da6a1d39f671d65` updates exactly 16
P1/P2 score segments across 14 observation rows. Reversing only those substitutions
reproduces the preceding Git blob byte-for-byte, including all 118 CRLF endings.
DeadSync commit `0e7e0fb6d` updates the fixture submodule pointer.

Fresh verification on the current DeadSync main source passed both complete
focused test binaries: `gameplay_score` (1 test) and `gameplay_underlay` (15 tests),
including the two previously failing snapshot tests. No runtime behavior changed
for this correction. The exact command, source hashes, snapshot hashes and test
counts are in `underlay-validation.json`; the retained Cargo output is in
`underlay-validation.log`.

Native and bundled source bytes match at SHA-256
`74bcc7cae175d34dbb44bd7f5037596faec3ce701f8673d7796e7cdd1b31b6a8`:

- `itgmania-harness/vendor/simply-love/BGAnimations/ScreenGameplay underlay/PerPlayer/Score.lua`
- `deadsync/crates/deadsync-song-lua/assets/simply-love/BGAnimations/ScreenGameplay underlay/PerPlayer/Score.lua`

This verifies the recorded score initialization and focused behavior. It does not
claim complete song-Lua or framebuffer parity.
