# Native routine failure isolation

These fresh harness 0.1.103 references use manual input in dance and pump routine. P1 is explicitly failed at music time 0.25s; the team is failed at 1.25s. The captures preserve five judgment callbacks, four presses and four releases. P1, P2 and the team retain independent failed flags and earned points. All compared values pass the [complete DeadSync replays](../routine-stats-replays/README.md).

Each game directory contains the exact Lua, simfile, audio, inputs, compressed native trace and capture logs. [Native assertions and hashes](native-validation.json) record the final statistics.
