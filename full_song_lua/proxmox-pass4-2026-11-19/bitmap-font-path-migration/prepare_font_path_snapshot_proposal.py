"""Propose one typed path spelling change; never write the real fixture."""
from pathlib import Path
import difflib
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "target/proxmox-song-lua-20261119/font-snapshot-path-evidence-20261119T043158Z"
before_receipt = json.loads((OUT / "before.json").read_text())
source = Path(before_receipt["source"])
fixture = Path(before_receipt["fixture"])
before = (OUT / "source-before.rs").read_bytes()
after = source.read_bytes()
newline = b"\r\n" if b"\r\n" in before else b"\n"
old = '\n'.join([
    '        } else {',
    '            reference_test::assert_debug(',
    '                "song/tests/rust_bitmap_text.rs::payload",',
    '                &(phase, &actual.unwrap()),',
    '            );',
]).encode().replace(b"\n", newline)
new = '\n'.join([
    '        } else {',
    '            let actual = actual.unwrap();',
    '            if let Some((_, path)) = &actual.font',
    '                && path.starts_with(self._files.path())',
    '            {',
    '                assert_eq!(path, &self._files.path().join("custom.ini"), "{phase}");',
    '            }',
    '            // Compare the observed physical path above; only its copied debug',
    '            // presentation uses portable separators in the frozen snapshot.',
    '            let mut snapshot = actual.clone();',
    '            if let Some((_, path)) = &mut snapshot.font {',
    '                *path = deadsync_song_lua::file_path_string(path).into();',
    '            }',
    '            reference_test::assert_debug(',
    '                "song/tests/rust_bitmap_text.rs::payload",',
    '                &(phase, &snapshot),',
    '            );',
]).encode().replace(b"\n", newline)
assert before.count(old) == 1
assert before.replace(old, new) == after, "source changes outside approved Pair.compare hunk"
assert fixture.read_bytes() == (OUT / "fixture-before.snap").read_bytes(), "fixture was modified"
original = fixture.read_bytes()
lines = original.splitlines(keepends=True)
test = None
case = 0
changed = []
old_path = b'"$FIXTURE0' + bytes([92, 92]) + b'custom.ini"'
new_path = b'"$FIXTURE0/custom.ini"'
for i, line in enumerate(lines):
    if line.startswith(b"test: "):
        test = line.removeprefix(b"test: ").strip().decode()
        case = 0
        continue
    if test == "font_resolution_and_builtin_fallback_match_production" and case == 8:
        assert b"label.Font='custom.ini'" in line and line.count(old_path) == 1
        updated = line.replace(old_path, new_path)
        lines[i] = updated
        changed.append({"test": test, "case": case, "line": i + 1,
                        "before": line.decode().rstrip("\r\n"),
                        "after": updated.decode().rstrip("\r\n"),
                        "field": "BitmapText.font.1 PathBuf debug separator only"})
    if test is not None:
        case += 1
assert len(changed) == 1
proposed = b"".join(lines)
assert original.count(old_path) == 1
assert proposed == original.replace(old_path, new_path), "unrelated fixture bytes changed"
def sha(data):
    return hashlib.sha256(data).hexdigest()
def save(name, data):
    path = OUT / name
    if path.exists():
        assert path.read_bytes() == data
    else:
        path.write_bytes(data)
    return {"path": str(path), "bytes": len(data), "sha256": sha(data)}
source_file = save("source-after.rs", after)
proposal_file = save("fixture-proposed.snap", proposed)
source_diff = ''.join(difflib.unified_diff(before.decode().splitlines(keepends=True), after.decode().splitlines(keepends=True), fromfile="source-before.rs", tofile="source-after.rs")).encode()
fixture_diff = ''.join(difflib.unified_diff(original.decode().splitlines(keepends=True), proposed.decode().splitlines(keepends=True), fromfile="fixture-before.snap", tofile="fixture-proposed.snap")).encode()
save("source-change.patch", source_diff)
save("fixture-proposal.patch", fixture_diff)
authority = []
for relative, regions in [
    ("crates/deadlib-lua/src/reference_test.rs", [[36, 72], [140, 149]]),
    ("crates/deadsync-song-lua/src/actors/assets.rs", [[31, 54], [157, 171]]),
    ("crates/deadsync-song-lua/src/files.rs", [[401, 415]]),
]:
    data = (ROOT / relative).read_bytes()
    authority.append({"source": relative, "regions": regions, **save("authority-" + Path(relative).name, data)})
source_patch = subprocess.check_output(["git", "diff", "--binary", "--full-index", "HEAD"], cwd=ROOT)
patch_file = save("source-after.patch", source_patch)
receipt = {
    "format_version": 1,
    "source_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "fixture_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT / "tests/fixtures", text=True).strip(),
    "source_before": before_receipt, "source_after": source_file, "source_patch_after": patch_file,
    "snapshot_before": {"sha256": sha(original), "bytes": len(original)}, "snapshot_proposal": proposal_file,
    "changes": changed, "changed_rows": 1, "all_unrelated_snapshot_bytes_equal": True,
    "all_other_source_bytes_equal": True, "runtime_state_or_payload_mutated": False,
    "global_normalizer_changed": False, "fixture_written": False, "tests_run": False,
    "authority": authority,
    "reason": "PathBuf.join adds the host separator. Prefix-only fixture normalization leaves that suffix untouched. The test now verifies the observed local physical PathBuf and formats only a copied font PathBuf with existing file_path_string. The sole expected debug spelling uses a portable slash.",
}
receipt_file = save("proposal.json", (json.dumps(receipt, indent=2) + "\n").encode())
print(json.dumps({"source": source_file, "fixture_proposal": proposal_file, "receipt": receipt_file,
                  "changed_rows": 1, "fixture_written": False, "unrelated_bytes_preserved": True}))
