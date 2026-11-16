# Recorded gameplay input repair

The DeadSync runner now sends recorded first presses and releases through production lane routing and judgment processing before delivering each Lua callback once. Recorded repeats remain callback-only. Native player/column observations check independently chosen DeadSync lanes; they do not choose notes or import native judgments.

Harness 0.1.103 supplies the original `Player::Step` timer reads. The later Lua `DeviceInput.ago` cannot reconstruct those reads. Row statistics still finalize on the next `Player::Update`; the [native phase control](../native-validation/pass3-native-input-phase/validation.json) verifies this ordering.

| Manual routine case | Historical 0.1.102 mismatches | Retained 0.1.103 replay mismatches | Errors | Inputs replayed | Replay |
| --- | ---: | ---: | ---: | ---: | ---: |
| Dance | 82 | 46 | 2 | 8 | 3.756s |
| Pump | 82 | 46 | 2 | 8 | 3.715s |

Both full replays now match all compared actual-point, W1 and miss fields. Each still has 28 recorded-life mismatches, 16 command/query event mismatches, one command/query count mismatch and one source broadcast count mismatch. `GetRoutineStageStats` is still missing and produces the two callback errors. These candidates are not accepted fixtures.

The historical and current columns use different native capture revisions of the same unchanged control source. The callback-only regression separately reproduces the input-routing defect. Both focused tests pass; the broader gameplay module passes all 75 tests, including those two. See [validation](../input-routing-validation.json), [exact-byte evidence](../input-routing-evidence.json), and the per-game reports.

Retained test-development failures distinguish the initial incorrect same-input score expectation, the incomplete overlay lookup, and the helper chart's 25ms timing calibration from production defects. The final test uses the chart's calibrated note time and checks native scoring phases without forcing row finalization during input.

Windows validation was not completed: the local debug build exhausted disk space. Linux validation and the targeted replays ran on Proxmox worker 1402.
