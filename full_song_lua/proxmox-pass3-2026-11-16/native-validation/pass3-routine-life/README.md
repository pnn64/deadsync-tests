# Native routine life controls

Fresh harness 0.1.103 captures against native revision `663525dcb86eb570d0ef6a2e209678436660ae26` confirm the same behavior for dance and pump routine. Each folder retains exact source bytes, the native trace and capture metadata; [evidence.json](evidence.json) records transport hashes.

| Phase | Shared meter, both getters | P1 recorded life | P2 recorded life |
| --- | ---: | ---: | ---: |
| Initial | 0.5 | 0 | 0 |
| P1 SetLife(0.8) | 0.8 | 0.5 | 0 |
| P2 SetLife(0.2) | 0.2 | 0.5 | 0.5 |
| Later update | 0.2 | 0.5 | 0.5 |

`GetLifeMeter(P1)` and `GetLifeMeter(P2)` return the same native object. Values above are rounded for readability; traces retain exact f32 values.

In the pinned native source, `Player::Load` writes initial history only for an individual life meter. `Player::ChangeLifeRecord` reads `m_fTugLifePercentP1` for a combined meter, rather than the inner shared meter's current value. Each Player writes its own history. These observations are the reference behavior, even when recorded history differs from the live meter.

The source uses autoplay to avoid score-driven life changes and makes explicit script writes at separate times. Pump uses its valid `default` noteskin. Initial launch errors (zero-based chart index, then missing pump noteskin) are retained under `setup-failures`; corrected captures use chart index 1 and the same authored Lua/simfile bytes.

These are native references, not accepted DeadSync archives. [DeadSync baselines](../../routine-life-baselines/README.md) isolate the remaining differences.
