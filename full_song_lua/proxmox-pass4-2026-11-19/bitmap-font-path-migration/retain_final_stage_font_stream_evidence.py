"""Prepare the reviewed fixture checkpoint without committing or touching product state."""
from pathlib import Path
import datetime
import difflib
import hashlib
import json
import subprocess
import zipfile

TASK = Path(__file__).resolve().parent
PRODUCT = TASK.parents[1]
FIXTURES = Path("C:/GitHub/deadsync-fixtures-lua-fleet-20261119")
EXPECTED_HEAD = "ea94a08090c60c9da30d72995c943796c6a96fca"
PREFIX = Path("full_song_lua/proxmox-pass4-2026-11-19")
DEST = FIXTURES / PREFIX
STAMP = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
OUT = TASK / ("final-stage-font-stream-fixture-preparation-" + STAMP)
SNAPSHOT = "regression-expectations/deadsync-song-lua/42b202d737540250.snap"
PROPOSAL = TASK / "font-snapshot-path-evidence-20261119T043158Z"
STAGE = TASK / "played-stage-native-evidence-20261119T042839Z"
STAGE_SHA = "bd025f6a208c93bc145f22115bb8e91c5307d726dff5e6a77d8b2c1b404acf1e"
STREAM = TASK / "stream-commit-b2af4f355d827fb0e89aead84b4c75a9b8cccf6c"

def sha(data):
    return hashlib.sha256(data).hexdigest()

def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])

def checked_bytes(path, expected=None):
    path = Path(path)
    assert path.is_file() and not path.is_symlink(), str(path)
    data = path.read_bytes()
    assert len(data) < 50_000_000, str(path)
    if expected:
        assert sha(data) == expected, (str(path), sha(data), expected)
    return data

def line_ending(data):
    if b"\r\n" in data:
        assert data.count(b"\n") == data.count(b"\r\n")
        return b"\r\n"
    return b"\n"

assert git(FIXTURES, "rev-parse", "HEAD").decode().strip() == EXPECTED_HEAD
assert not git(FIXTURES, "status", "--porcelain", "--untracked-files=all").strip(), "fixture worktree must start clean"
product_before = {
    "head": git(PRODUCT, "rev-parse", "HEAD").decode().strip(),
    "working_patch_sha256": sha(git(PRODUCT, "diff", "--binary", "--full-index", "HEAD")),
    "index_patch_sha256": sha(git(PRODUCT, "diff", "--cached", "--binary", "--full-index")),
    "fixture_head": git(PRODUCT / "tests/fixtures", "rev-parse", "HEAD").decode().strip(),
}
assert sha(checked_bytes(PRODUCT / "crates/deadsync-song-lua/tests/bitmap_text.rs")) == "201993bbaca56b7fc67142784f839df1185dda4a7cec1ac220f5d9704484d6f9"
proposal_receipt = json.loads(checked_bytes(PROPOSAL / "proposal.json", "0a1e2ebc73acf8463bf4b7f9fdd55545718a09d25d2aba431f590ed28146adc6"))
assert proposal_receipt["changed_rows"] == 1 and proposal_receipt["all_unrelated_snapshot_bytes_equal"]
original = checked_bytes(PROPOSAL / "fixture-before.snap", "b8d7ed19e6ed6fa8b36a10c430b773037f032a805e45dfd9b08ce51546f1b632")
proposed = checked_bytes(PROPOSAL / "fixture-proposed.snap", "f0844e36a2840e15c8c6ee574848cb8d2808e6ae073ab5f386905e9f05a83b79")
assert git(FIXTURES, "show", "HEAD:" + SNAPSHOT) == original
old_path = b'"$FIXTURE0' + bytes([92, 92]) + b'custom.ini"'
assert original.count(old_path) == 1
assert original.replace(old_path, b'"$FIXTURE0/custom.ini"') == proposed
before_lines = original.splitlines(keepends=True)
after_lines = proposed.splitlines(keepends=True)
assert len(before_lines) == len(after_lines)
changed_lines = [i + 1 for i, (a, b) in enumerate(zip(before_lines, after_lines)) if a != b]
assert changed_lines == [26]
assert b"label.Font='custom.ini'" in before_lines[25]
snapshot_path = FIXTURES / SNAPSHOT
if snapshot_path.exists():
    assert checked_bytes(snapshot_path) == original
snapshot_index_before = git(FIXTURES, "ls-files", "-v", "--", SNAPSHOT).decode().strip()
assert snapshot_index_before.endswith(" " + SNAPSHOT)

pending = {}
origins = {}
def retain(source, relative, expected=None):
    data = checked_bytes(source, expected)
    name = (PREFIX / relative).as_posix()
    assert name not in pending and not (FIXTURES / name).exists(), name
    pending[name] = data
    origins[name] = {"source": str(Path(source).resolve()), "bytes": len(data), "sha256": sha(data)}

def retain_tree(source, relative):
    source = Path(source)
    assert source.is_dir() and not source.is_symlink()
    for path in sorted(source.rglob("*")):
        assert not path.is_symlink(), str(path)
        if path.is_file():
            retain(path, Path(relative) / path.relative_to(source))

retain_tree(PROPOSAL, "bitmap-font-path-migration/proposal")
retain(TASK / "prepare_font_path_snapshot_proposal.py", "bitmap-font-path-migration/prepare_font_path_snapshot_proposal.py")
retain(Path(__file__), "bitmap-font-path-migration/retain_final_stage_font_stream_evidence.py")
retain(STAGE / (STAGE_SHA + ".zip"), "played-stage-native/played-stage-native-evidence.zip", STAGE_SHA)
retain(STAGE / (STAGE_SHA + ".manifest.json"), "played-stage-native/manifest.json", "3e29fe953d8f02344fc19c38900015f5a9bc3435f8e50661d5560ea9478291c3")
retain(STREAM.with_suffix(".zip"), "stream-finalization/stream-commit-b2af4f3.zip", "6d04922f6b5d4737a958a0df96e49b080b556f3cd04f2675d59a820d2e0951c7")
retain(STREAM / "manifest.json", "stream-finalization/manifest.json")
retain(STREAM / "attestation.json", "stream-finalization/attestation.json", "a1876857a2b47c6a3712489ec72a215afedf3dcc6469056fced2946fafb8f37b")
with zipfile.ZipFile(STREAM.with_suffix(".zip")) as archive:
    assert archive.read("manifest.json") == checked_bytes(STREAM / "manifest.json")
    assert archive.read("attestation.json") == checked_bytes(STREAM / "attestation.json")
stream_attestation = json.loads(checked_bytes(STREAM / "attestation.json"))
assert stream_attestation["harness_commit"] == "b2af4f355d827fb0e89aead84b4c75a9b8cccf6c"
assert stream_attestation["git_tree"] == "b94ed50e020d6c5d7f2bd0e939438c9c14c55038"
assert stream_attestation["compiled_source_files_verified"] == 409
font_scope = TASK / "genshin-evidence/font-alias-scope"
scope = json.loads(checked_bytes(font_scope / "scope.json"))
for item in scope["native_authorities"] + scope["product_source_snapshot"] + [scope["full_bitmap_target_at_this_checkpoint"]["log"]]:
    assert len(checked_bytes(item["path"], item["sha256"])) == item["bytes"]
retain_tree(font_scope, "font-file-alias/font-alias-scope")
retain(TASK / "genshin-evidence/diagnosis.json", "font-file-alias/diagnosis.json")

evidence_path = DEST / "evidence-files.json"
evidence_before = checked_bytes(evidence_path)
existing = json.loads(evidence_before)
assert len({row["path"] for row in existing}) == len(existing)
for row in existing:
    assert len(checked_bytes(FIXTURES / row["path"], row["sha256"])) == row["bytes"]
assert not set(pending) & {row["path"] for row in existing}
verifier_path = DEST / "verify_evidence.py"
verifier_before = checked_bytes(verifier_path)
vnl = line_ending(verifier_before)
verifier = verifier_before.replace(vnl, b"\n").decode()
old_bundles = '''        ("native-validation/validated-capture-evidence.zip", "native-validation/validated-manifest.json", True),
        ("native-validation/clock-control-failed-exercise.zip", "native-validation/failed_exercise-manifest.json", True),
        ("pipeline-baselines/life-pipeline-evidence.zip", "pipeline-baselines/manifest.json", True),
        ("native-life-score/life-event-score-evidence.zip", "native-life-score/manifest.json", True),
        ("native-life-score-glx/life-event-score-glx-evidence.zip", "native-life-score-glx/manifest.json", True),
        ("repaired-native-controls/replay-evidence.zip", "repaired-native-controls/manifest.json", True),
        ("negative-native-evidence/negative-evidence.zip", "negative-native-evidence/manifest.json", False),'''
new_bundles = old_bundles.replace(", True)", ', "embedded")').replace(", False)", ', "verification")') + '''
        ("played-stage-native/played-stage-native-evidence.zip", "played-stage-native/manifest.json", "external"),
        ("stream-finalization/stream-commit-b2af4f3.zip", "stream-finalization/manifest.json", "embedded"),'''
assert verifier.count(old_bundles) == 1
verifier = verifier.replace(old_bundles, new_bundles)
for old, new in [
    ('    for archive_name, manifest_name, embedded_manifest in bundles:\n',
     '    for archive_name, manifest_name, layout in bundles:\n        embedded_manifest = layout == "embedded"\n'),
    ('        members = manifest["files"]\n',
     '        members = manifest["members"] if layout == "external" else manifest["files"]\n        member_key = "archive_path" if layout == "external" else "path"\n'),
    ('            indexed = {item["path"]: item for item in members}\n',
     '            indexed = {item[member_key]: item for item in members}\n'),
    ('            else:\n                assert json.loads(archive.read("verification.json")) == manifest["verification"], archive_name\n',
     '            elif layout == "verification":\n                assert json.loads(archive.read("verification.json")) == manifest["verification"], archive_name\n            else:\n                assert layout == "external", layout\n'),
]:
    assert verifier.count(old) == 1, old
    verifier = verifier.replace(old, new)
verifier_after = verifier.encode().replace(b"\n", vnl)
assert line_ending(verifier_after) == vnl
compile(verifier_after, str(verifier_path), "exec")
readme_path = DEST / "README.md"
readme_before = checked_bytes(readme_path)
rnl = line_ending(readme_before)
addition = '''

## Additional committed-stage, font and streaming evidence

`played-stage-native/` retains 181 original evidence members and their external
manifest. Its final Cold, Vtubers, MODULO and Genshin chart 3 reports all pass
both production and diagnostic replay with zero mismatches or errors, while
retaining `whole_song_parity_proven=false` and every pending-coverage limit.
These reports used DeadSync `23c79b2fb64f2467f0b2afe3e7b3aa1eecf90aa5`, working
patch SHA-256 `693e51d4a7d5ebb8afd0cd11e108ea68e2c6fba3a080908e587b365825a808b6`,
and fixture revision `0a49b80d8dd1cbc59d86ac764e739537fcc1a79b`. Complete
statistics and transitions passed 12 and 25 tests respectively. The earlier
full playback gate passed 233 tests with three existing ignored tests under
its own retained source identity. The original natural completion failures,
sampler failures and failed BitmapText snapshot checks remain in the ZIP.
The reviewed history/reload subset was subsequently committed as
`4224b3b2eb5dbc0efd15618bf86266bb651af56c`; its staging proof is retained.
The four large original native archives are identified by exact size and
SHA-256 in the unchanged external manifest and are not duplicated here.

`font-file-alias/` preserves the original Genshin diagnosis, pinned native
Font/File selection authority, product source and the first corrected test
log. Its historical pending replay status is superseded only for chart 3 by
the final report above; raw glyph geometry and pixel coverage remain pending.
`bitmap-font-path-migration/` retains the approved test-only presentation
change and a single expected PathBuf separator change for relative custom.ini.
The actual local font path is asserted before a copied payload is formatted;
the runtime, global snapshot normalizer and every unrelated expected byte are
unchanged. Final Windows and Linux full-target gates remain pending at this
fixture preparation checkpoint.

`stream-finalization/` preserves committed harness
`b2af4f355d827fb0e89aead84b4c75a9b8cccf6c`, the original ZIP, its byte-identical
embedded/external manifest and the separate original attestation. The commit
matches all 409 compiled source blobs. Its 229 unit tests, native byte/error
equivalence control and completed Kaboom capture/archive under the unchanged
6 GiB cap passed. Large Kaboom inputs and outputs remain referenced by their
exact guest paths and hashes. This evidence does not claim deployment to the
fleet or completion of candidate B's combined production profile gate.
'''
assert b"## Additional committed-stage, font and streaming evidence" not in readme_before
readme_after = readme_before + addition.encode().replace(b"\n", rnl)

OUT.mkdir()
for name, data in [("evidence-files.before.json", evidence_before), ("verify_evidence.before.py", verifier_before),
                   ("README.before.md", readme_before), ("snapshot.before.snap", original)]:
    (OUT / name).write_bytes(data)
application = {
    "schema_version": 1, "fixture_parent": EXPECTED_HEAD, "created_at": STAMP,
    "snapshot": {"path": SNAPSHOT, "before_sha256": sha(original), "after_sha256": sha(proposed),
                 "changed_lines": changed_lines, "changed_test": "font_resolution_and_builtin_fallback_match_production",
                 "changed_case": 8, "all_unrelated_bytes_equal": True, "index_entry_before": snapshot_index_before},
    "proposal_receipt_sha256": sha(checked_bytes(PROPOSAL / "proposal.json")),
    "product_before": product_before, "product_files_modified": False,
    "retained_files": origins,
    "original_manifests_retained_byte_for_byte": True,
    "large_native_inputs_copied": False, "acceptance_fields_changed": False,
    "commit_or_push_performed": False,
}
application_name = (PREFIX / "bitmap-font-path-migration/application-receipt.json").as_posix()
application_bytes = (json.dumps(application, indent=2) + "\n").encode()
assert application_name not in pending and not (FIXTURES / application_name).exists()
pending[application_name] = application_bytes
additions = [{"path": name, "bytes": len(data), "sha256": sha(data)} for name, data in sorted(pending.items())]
enl = line_ending(evidence_before)
end = enl + b"]" + enl
assert evidence_before.endswith(end)
addition_body = json.dumps(additions, indent=2).encode().replace(b"\n", enl)
assert addition_body.startswith(b"[" + enl) and addition_body.endswith(enl + b"]")
evidence_after = evidence_before[:-len(end)] + b"," + enl + addition_body[len(b"[" + enl):-len(enl + b"]")] + end
assert json.loads(evidence_after) == existing + additions
assert evidence_after.startswith(evidence_before[:-len(end)] + b",")
assert line_ending(evidence_after) == enl

# The only index operation is the explicitly authorized tracked snapshot's
# manual skip-worktree bit; sparse patterns and the product checkout are untouched.
assert git(FIXTURES, "rev-parse", "HEAD").decode().strip() == EXPECTED_HEAD
assert not git(FIXTURES, "status", "--porcelain", "--untracked-files=all").strip()
git(FIXTURES, "update-index", "--no-skip-worktree", "--", SNAPSHOT)
snapshot_path.parent.mkdir(parents=True, exist_ok=True)
snapshot_path.write_bytes(proposed)
for name, data in pending.items():
    destination = FIXTURES / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as stream:
        stream.write(data)
for path, before, after in [(evidence_path, evidence_before, evidence_after),
                            (verifier_path, verifier_before, verifier_after),
                            (readme_path, readme_before, readme_after)]:
    assert path.read_bytes() == before, str(path)
    path.write_bytes(after)
for name, data in pending.items():
    assert checked_bytes(FIXTURES / name) == data
assert checked_bytes(snapshot_path) == proposed
product_after = {
    "head": git(PRODUCT, "rev-parse", "HEAD").decode().strip(),
    "working_patch_sha256": sha(git(PRODUCT, "diff", "--binary", "--full-index", "HEAD")),
    "index_patch_sha256": sha(git(PRODUCT, "diff", "--cached", "--binary", "--full-index")),
    "fixture_head": git(PRODUCT / "tests/fixtures", "rev-parse", "HEAD").decode().strip(),
}
assert product_before == product_after, "product identity changed during fixture preparation"
handoff = {
    "fixture_parent": EXPECTED_HEAD, "evidence_directory": str(DEST), "preparation_receipt_directory": str(OUT),
    "new_evidence_files": additions, "old_evidence_count": len(existing), "new_evidence_count": len(existing) + len(additions),
    "changed_tracked_files": [{"path": str(path.relative_to(FIXTURES)), "before_sha256": sha(before),
                               "after_sha256": sha(after), "after_bytes": len(after)}
                              for path, before, after in [(snapshot_path, original, proposed),
                                                         (evidence_path, evidence_before, evidence_after),
                                                         (verifier_path, verifier_before, verifier_after),
                                                         (readme_path, readme_before, readme_after)]],
    "product_before": product_before, "product_after": product_after, "product_unchanged": True,
    "verification_pending": True,
}
(OUT / "handoff.json").write_text(json.dumps(handoff, indent=2) + "\n", encoding="utf-8")
for name, before, after in [("verifier", verifier_before, verifier_after), ("README", readme_before, readme_after),
                            ("snapshot", original, proposed)]:
    diff = ''.join(difflib.unified_diff(before.decode().splitlines(keepends=True), after.decode().splitlines(keepends=True), fromfile=name + ".before", tofile=name + ".after"))
    (OUT / (name + ".patch")).write_bytes(diff.encode())
print(json.dumps({"prepared": True, "receipt": str(OUT / "handoff.json"),
                  "new_evidence_files": len(additions), "evidence_files": len(existing) + len(additions),
                  "total_new_evidence_bytes": sum(row["bytes"] for row in additions),
                  "snapshot_sha256": sha(proposed), "product_unchanged": True,
                  "verifier_sha256": sha(verifier_after), "evidence_manifest_sha256": sha(evidence_after)}))
