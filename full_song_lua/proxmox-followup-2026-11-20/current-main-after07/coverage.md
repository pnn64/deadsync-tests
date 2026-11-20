Completed after07 coverage inventory, source commit `af6a6c9e045f5dfb13abe38bd4eb58d7326f2e26`.

Runner SHA-256: `69fe4fb89667c2a41ac4b80f589b0722b37fb72c197f50ac09948337271ac691`. All five execution receipts completed with exit 0 and bind to this exact build. No earlier replay is substituted.

| Case | Reference frames | Stage fields D / P | Draws D / P | Vertices D / P | Draw mismatches D / P | Pending combined / production |
|---|---:|---:|---:|---:|---:|---:|
| typed-aft-uv | 537 | 2,038 / 2,038 | 450 / 450 | 2,700 / 2,700 | 0 / 0 | 35 / 7 |
| amv-color | 559 | 2,088 / 2,088 | 2,380 / 2,380 | 14,280 / 14,280 | 0 / 0 | 35 / 7 |
| wrapper-removal | 581 | 2,158 / 2,158 | 1,300 / 1,300 | 7,800 / 7,800 | 0 / 0 | 35 / 7 |
| sharkmode | 2,258 | 12,453 / 12,453 | 5,190 / 5,190 | 62,940 / 62,940 | 0 / 0 | 35 / 7 |
| pernicious-deed | 7,447 | 36,244 / 36,244 | 224,479 / 224,479 | 876,144 / 876,144 | 0 / 0 | 35 / 7 |

| Case | Diagnostic native / owned queries | Uncompared owned queries | Random D replayed / captured | Random P replayed / captured | Text content D / P | Gameplay inputs D / P |
|---|---:|---:|---:|---:|---:|---:|
| typed-aft-uv | 11 / 11 | 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| amv-color | 61 / 61 | 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| wrapper-removal | 364 / 364 | 0 | 12 / 12 | 12 / 12 | 0 / 0 | 0 / 0 |
| sharkmode | 23,123 / 23,123 | 3 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| pernicious-deed | 213,684 / 213,684 | 0 | 496 / 496 | 496 / 496 | 34,920 / 34,920 | 0 / 0 |

Focused regressions: **301 passed, 0 failed, 3 ignored**. Interactive comparator regressions: **26 passed, 0 failed, 0 ignored**. Combined: **327 passed, 0 failed, 3 ignored**.

Combined archives accepted: 5/5; diagnostic checks passed: 5/5; production gameplay checks passed: 5/5. Nested standalone production archive-acceptance flags are true in 0/5 cases; this is a separate acceptance scope.

D and P mean separate diagnostic and production replay paths. They replay the same reference frames; stage-field totals at the report root include both paths. Production command/query instrumentation is absent, so production query counts are null rather than a claimed zero.

Draw samples count native submissions, not unique Actor.Draw calls. Vertices count the comparator's owned expanded rows, not raw native quad vertices. Batched submissions and offscreen/degenerate equivalences remain separate counters in the JSON.

Production gameplay checks and combined archive acceptance are separate from the nested standalone production archive-acceptance flag. All three flags are retained individually in the JSON.

Actual parity-proof flag values across the cases (D/P separately): `{"pixel_parity_proven": {"diagnostic": [false], "production": [false]}, "production_parity_proven": {"diagnostic": [false], "production": [false]}, "whole_song_parity_proven": {"diagnostic": [false], "production": [false]}}`.

Coverage obligations are not failed comparisons. Each case retains the exact operation/resource buckets, missing subscriber identities, and production obligations; global pending remains separate. Production obligations:

- Entry counts: 35 combined = 28 diagnostic + 7 production; diagnostic groups contain 1 operation bucket(s), 1 resource bucket(s), and 26 missing subscriber identities.

- application build without test-support
- full-song completion
- sampled framebuffer pixels
- production command/query instrumentation
- complete stage finalization, aggregate/evaluation history and public STATSMAN:Reset
- saved statistics getter functions explicitly invoked with another stage's player receiver
- BitmapText submitted glyph geometry, texture bindings and RGBA (live text content is compared)

Native natural gameplay exit and complete recorded-frame replay do not establish the application build, complete input coverage, glyph geometry or framebuffer pixels. Text counters cover content only. Comparator regression counts are not captured input events.

Historical after04/after05/after06 results and fleet accounting are excluded. Exact report, execution, invocation, regression-log, build and source hashes are in the companion JSON.
