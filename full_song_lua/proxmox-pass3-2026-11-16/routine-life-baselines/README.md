# Routine life replay baselines

Both fresh native controls replay completely with the input-routing repair. Each has **32 mismatches and zero callback errors**: 28 recorded-life samples and four authored broadcasts. Neither archive is accepted.

The broadcasts expose three missing behaviors: both routine players must receive the same life-meter object; a script write must update that shared meter immediately for both getters; each player's recorded history remains separate from that meter and from the other player's history. DeadSync currently exposes separate meter objects, updates the other meter on a later frame, and copies live meter values into both histories.

Dance replay took 3.626s; pump took 3.721s on the eight-vCPU worker, excluding capture/build/setup. See [native controls](../native-validation/pass3-routine-life/README.md), [validation](../input-routing-validation.json), and [transport hashes](evidence.json). These are focused supplemental diagnostics, outside the 503-primary ledger.
