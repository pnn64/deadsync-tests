# Audit tooling

These scripts document this audit's execution and verification. They are not a replacement for the repositories' supported test commands.

Guest scripts expect Linux, Python 3, `ijson`, `zstandard`, systemd, passwordless sudo for the `parity` audit account, ffprobe/ffmpeg, and the original layout under `/opt/song-lua-audit`. `worker.py` expects the pinned executables under `bin`, the harness/native source trees, the frozen corpus under `Songs`, and results under `results`. The original script arguments and stage limits are retained in the result JSON records.

`remote.py` is a local SSH helper. Operational controllers used it from the original Windows audit directory (`C:/GitHub/deadsync/target/proxmox-song-lua-20261115`) alongside `fleet.json`, `retry-vm.json`, task `known_hosts`, manifests and other state. Copying it into this report does not recreate those credentials or launch any services. No private keys are included.

For reproduction, prefer the recorded command and a retained candidate archive rather than rerunning fleet provisioning or queue controllers. The main report explains compressed/raw SHA256 verification and the required content-addressed `.tar` filename. All source commits and binary hashes are pinned in provenance.json. The fixtures are diagnostic inputs, and comparison acceptance has the coverage limits described in the report.

The entrypoint probes stop at beat 4 and are loading diagnostics only. The guarded-profile controls, Bank Account versus control and stopped-GC Velvet control run whole songs under their separately recorded profiles. Reduced movie decoder and initial effect-clock controls establish specific mechanisms, not full-song parity.

`check-audit-tools.py` runs the audit-tool checks. `verify-results.py` verifies guest corpus, binaries and retained artifacts; `check-fleet-processes.py` checks source pins and remaining task processes. These tools do not patch product code.
