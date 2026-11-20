# Final frozen-build fleet accounting

This is the terminal accounting of the original fleet and its declared retry
contracts. It uses runner SHA-256
`90abd15f5e2f6e15a23b33faacc83ec81bde13a2f709f095576a10ce0c8405e4`;
it is not a fresh corpus replay of the current DeadSync main branch.

The collector read all 15 workers successfully after the original retry roles
were restored. The exact snapshot is bound by SHA-256
`546c9b576e4a90023530d0be5deeb2fe52ef8667f95d8375508ec7a100010e35`.
Its immutable summary and the subsequent strict accounting join are retained.

| Accounting measure | Count |
| --- | ---: |
| Original known jobs | 1,620 |
| Original jobs with terminal evidence | 1,620 |
| Final accepted combined diagnostic/production checks | 1,092 |
| Jobs with complete native data, including retries | 1,409 |
| Normal native captures complete | 1,381 |
| Additional complete retry captures | 28 |
| Normal submitted-comparison parity failures | 161 |
| Declared selected retry obligations, all terminal | 54 |
| Declared retry attempts, all terminal | 81 |
| Preserved predecessor failure outcomes | 27 |
| Jobs recovered by the explicit recovery policy | 2 |
| Outside-contract resource obligations still pending | 108 |
| Whole-song parity proofs | 0 |

The strict helper ran with `--require-complete` unchanged and returned **exit 2**,
with `complete=false`. All original jobs and declared attempts are terminal,
but 108 later resource failures remain outside a retry contract. They are
terminal OOM outcomes at a 6 GiB stage limit, each with exit 137: 53 native
capture failures and 55 replay failures. All 100 cases in the older checkpoint
remain; the final collection adds five capture and three replay cases. These
are separate from the seven role9458 replay OOM outcomes at a 12 GiB stage
limit. No pending case is relabeled as accepted or silently dropped.

The 54 selected retry outcomes are five passes, 13 replay errors, 20 native Lua
or setup errors, four capture resource failures, ten replay resource failures,
one capture validation/infrastructure error, and one capture timeout. These
are retry-contract outcomes; they must not be added to the original-job total
or treated as the results of the new main-branch fixes.

`accounting-summary.json` contains the exact counters and scope. The compressed
ledger contains all 1,620 rows. Invocation, execution, stdout/stderr, retained
input hashes, terminal retry collection, recovery receipts, and resource audits
are bound by the original `bundle-manifest.json`; all 18 delivered bundle files
were verified byte-for-byte before copying here. Full original inputs remain at
the recorded immutable paths. The original bundle manifest is preserved without
modification; this explanatory README is additional.

After this checkpoint, unused worker guests were gracefully parked. See the
adjacent resource-cleanup evidence for that later action. Accepted implemented
comparisons do not prove full-song behavior, framebuffer pixels, or the current
application without test-support instrumentation; individual replay reports
retain their pending coverage.
