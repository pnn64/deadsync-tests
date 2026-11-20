# Native replay checkpoint after07

This checkpoint binds the tested source to DeadSync commit af6a6c9e045f5dfb13abe38bd4eb58d7326f2e26.
Every changed source file was checked against the completed build identity.
Every current replay and regression receipt was checked against that same
build and its exact executable. No result is carried across builds.
The exact source patch, executable identities, reports, execution receipts,
logs and focused regression results are preserved in evidence.zip.

summary.json separates diagnostic and production results, retains all pending
coverage, and records total draw mismatch counters even when example lists
are capped. An accepted recorded replay is not a claim of whole-song,
production-build or framebuffer-pixel parity. Supplementary earlier runs
and correction proofs are historical evidence, excluded from current
validation totals and any claim of executable equivalence. Earlier checkpoints remain
unchanged.

Read coverage.md for exact measured counts and pending coverage. Read
remaining-source-gaps.md for the two source-identified gaps and ignored-test
requirements. These readable reports are also preserved within the evidence ZIP.
