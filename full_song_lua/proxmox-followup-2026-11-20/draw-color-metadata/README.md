# Recorded draw color metadata

The draw snapshot records the incoming diffuse and glow separately from geometric
ancestors. Exactly 630 field pairs were added across 39 of 48 observation rows.
Removing those fields reproduces the separately corrected scalar baseline byte
for byte, including all 61 CRLF line endings.

Three earlier internal render expectations used redundant scalar zoom aliases
1.25, 1.75 and 3.0. Existing live-scale normalization stores those values in axis
scales and neutralizes the scalar alias to 1.0. The retained native/owned source
proof and exact three-field patch establish this independent correction.

The normal compiled draw test executable passes all 12 original tests against
the resulting fixture. The archive retains every snapshot stage, byte proof,
failed helper attempt, corrected helper, exact compiled-library provenance and
validation receipt. New playback-test corrections for native inactive-glow
defaults are retained as test-setup evidence; their rebuilt execution is covered
by the later current-main checkpoint.
