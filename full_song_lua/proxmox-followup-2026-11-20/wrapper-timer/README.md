# Newly created wrapper effect timers

The latest native capture proves that a late wrapper and a nested wrapper both
start GetSecsIntoEffect at zero. Their 16 subsequent callbacks each follow
foreground song-clock advance exactly. The source, capture, input and trace
identities are retained in evidence.json.

The correction changes only seven timer values in four cumulative observation
rows of 9bff049c34306da7.snap. All other bytes, including all 46 CRLF line endings,
are preserved. Later timer progression already matched native behavior.

All eight wrapper regressions pass with the corrected reference. The exact test
command, binary identity and compiled source binding are in evidence.json; its
stdout and empty stderr are retained alongside it. This reference correction does
not claim complete parity for the wider native control: its after04 production
replay passes, while four deliberately caught stale Actor.x calls still expose
eight diagnostic observer mismatches. Those are retained separately and must be
resolved before accepting that whole control archive.
