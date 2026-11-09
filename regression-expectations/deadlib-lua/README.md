# Interpreter regression expectations

These fixtures replace live reference-runtime calls in interpreter tests. The
tests execute `deadlib-lua`; reading an expectation neither loads another Lua
runtime nor regenerates expected results from the implementation under test.

The initial observations were captured separately from Lua 5.1.5 through
`mlua` 0.12.2, using the existing comparison programs and assertions. The
optimized MSVC reference configuration was retained for native argument-check
ordering. Accepted observations passed the original comparison assertions;
temporary-path cases were recaptured with explicit path registration.

Each `.snap` file starts with its comparison-helper identity. A `test:` line
begins a test's consecutive observations. Remaining lines are complete Rust
`Debug` representations of the original scalar observations, including number
bits, nil slots, byte strings and diagnostics. File names are stable hashes of
the helper identity; the first line identifies the corresponding test source.

Only explicitly registered temporary paths are replaced with `$FIXTURE` labels.
The same path's shortened Lua debug and lexer source IDs are normalized too.
Other diagnostic bytes, caller names, argument numbers and line numbers remain
literal expectations. Fixed-name source-truncation tests remain unnormalized.

Bytecode fixtures include the input program's length and digest before its
original wire bytes. Writer fixtures retain block boundaries and empty writes;
source-rejection fixtures preserve the original corpus selection. An input
mismatch fails instead of loading an old image for a changed program.

The reader rejects missing cases and duplicate identities. There is no automatic
update mode. Changes to input programs or observations require reviewing the
corresponding expectations.
