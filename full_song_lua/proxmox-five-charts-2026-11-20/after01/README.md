# Five authored song chart parity checks

All five fresh native captures pass their implemented production and diagnostic comparisons with no mismatches or errors.

The exact tested uncompressed archives were packed by harness `b2af4f355d827fb0e89aead84b4c75a9b8cccf6c` using its actual zstd level 12. Decompressed hashes and byte counts match the tested candidates.

| Chart | Native frames | Native draw samples |
|---|---:|---:|
| Nishi-Shinjuku seisou kyoku | 2093 | 482 |
| Circles (native title Episode 15) | 2822 | 19110 |
| [CRYSTAL_ACCESS] | 2385 | 0 |
| And Drugs | 1689 | 0 |
| Flying Castle | 1754 | 0 |

Each case evidence ZIP preserves every completed replay stage, including historical-reference comparisons where present, their source/binary bindings, native capture and source proofs, resource receipts, and official pack provenance. Shared evidence retains chart selection, cleanup, focused regression results and source analysis.

Original recorded failures, fresh-capture baseline results and historical-reference replays remain distinct in summary.json. A newly captured native cadence can change whether the old runtime exhibits the recorded fault; a passing fresh baseline is not reported as a newly repaired failure.

Acceptance covers the checks implemented by the replay. Full pending coverage and original parity claim flags remain in summary.json and the unmodified reports; this does not establish framebuffer pixel parity or all unobserved behavior.
