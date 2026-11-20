# Pre-fix replay evidence

These runs use the retained DeadSync binary whose SHA-256 is
`db462d6906c1c904b7a786483e0719d09cc7fb120d73a9bf0df12ed3da7a1e25`.
It includes the AFT comparison correction, later committed as `a29b55646`,
but predates the AMV color, wrapper removal, and Wave metric fixes.

Sharkmode completed diagnostic and production replay with 16 submitted-draw
mismatches on each path. Pernicious Deed's full run stopped during diagnostic
replay at the later vibration input and did not reach production replay.
Its separate diagnostic prefix through 320 seconds completed 7,073 of 7,447
native frames, reported 20,032 mismatches, and retained both earlier callback
errors: missing Wave metrics and unimplemented RemoveWrapperState.
The prefix cannot establish archive acceptance or full-song parity.

`evidence.zip` retains the exact invocation, report (when produced), execution
receipt, and stdout/stderr for each run. `manifest.json` binds every member and
the checked archive. `summary.json` provides counts and error details without
discarding the full reports.
