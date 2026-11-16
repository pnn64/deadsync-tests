# Native routine input clocks

These are fresh harness **0.1.103** captures of the unchanged [dance and pump
manual controls](../routine-manual-controls/README.md). They are native-only
evidence, not accepted DeadSync parity fixtures.

Both captures retain eight physical input events and sixteen `Player::Step`
clock observations. Each event reaches both routine players; native ownership
still determines which notes score. P1 finishes with two W1s, P2 with two W1s
and one intentional miss, and the team with eight actual dance points.

`step_clock_inputs` preserves the original music position, rate and timer reads
before note selection or scoring. Player/column fields check independent replay
routing; they must not select DeadSync notes or supply judgments. The existing
Lua callback event timestamp is observed later and cannot replace these reads.

The [validation record](../input-clock-validation.json) contains source revisions,
hashes, native capture times, and test results: 216 Windows tests, 215 Linux tests,
and the native press/release regression in both callback modes. The regression
rejects the previous native binary because it lacks these clocks. Original
0.1.102 traces and their failing DeadSync reports remain unchanged.
