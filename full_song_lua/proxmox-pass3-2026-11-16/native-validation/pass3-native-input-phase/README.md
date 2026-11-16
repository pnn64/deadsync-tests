# Native input scoring phase

The ignored native regression passes with and without a Lua input callback. With the callback installed, the press observes zero actual points and zero W1 judgments; the later release observes five actual points and one W1. `Player::Step` records the note result immediately, while `Player::UpdateJudgedRows` finalizes row statistics on the next update.

The test source is harness commit `9052412e056853ce94e0aa6e2c8e6e5fb89fea3e`. The trace binary is the unchanged 0.1.103 input-clock build. [validation.json](validation.json) identifies both raw trace hashes and the test source hash; the two compressed traces preserve full native observations.
