# Native replay checkpoint after the first verified runtime fixes

This checkpoint binds the tested source to DeadSync commit c715e619dd5acba3ecacfaafc99fbc1981b8ec02.
The executable was built from the recorded earlier main commit plus its exact
retained worktree patch. The source was unchanged throughout the successful
build and its source-file hashes were checked again before committing.

The archive retains every report, invocation, execution receipt, output log,
compiled source binding, focused regression result and bounded geometry source
audit. summary.json separates diagnostic and production results, records exact
draw mismatch counts and retains all pending coverage entries. Individual report
mismatch lists can be capped; the draw_mismatches counters are the totals.

This is a measured checkpoint, including known failures. It does not assert
whole-song, production-build or framebuffer-pixel parity. Later fixes must be
validated in a new checkpoint; these reports and hashes remain unchanged.
