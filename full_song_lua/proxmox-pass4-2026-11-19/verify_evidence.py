"""Verify the exact native evidence checkpoint without extracting ZIP members."""
import hashlib
import json
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parent
REPOSITORY = ROOT.parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()



def original_byte_recovery():
    # Only these reviewed historical copies have Git-normalized line endings.
    folder = ROOT / "final-addendum/portable-evidence-original-bytes"
    manifest_raw = (folder / "manifest.json").read_bytes()
    archive_raw = (folder / "evidence.zip").read_bytes()
    assert digest(manifest_raw) == "10963583ffc9fdded187c82f73f2c251ffa5b04d7f8afbfcd77bb95a9b238530"
    assert len(archive_raw) == 198268
    assert digest(archive_raw) == "42b777470b0be39339ac3a36f7e9abbce4b9c1aadd0f2ea2ab0b6b7118239cba"
    manifest = json.loads(manifest_raw)
    assert manifest["historical_fixture_commit"] == "11f6edff529423df9ffef9458e93f7726183a646"
    assert manifest["historical_manifest_sha256"] == "f6e8576ae742e41fda910a386ca459502d83afbeaf527ae7d7104c0c25d56b7f"
    expected = {
        "live-visual-path-migration/" + state + "/" + name
        for state in ("original", "proposed")
        for name in ("live_visuals.rs", ".gitattributes", "28e74d92d026cc0b.snap", "b3216bc62d36e29c.snap", "be88a6d727933ed4.snap")
    }
    rows = {row["path"]: row for row in manifest["files"]}
    assert len(rows) == len(manifest["files"]) == 10 and set(rows) == expected
    result = {}
    with zipfile.ZipFile(folder / "evidence.zip") as archive:
        names = archive.namelist()
        assert len(names) == len(set(names)) and set(names) == expected | {"manifest.json"}
        assert archive.read("manifest.json") == manifest_raw
        for name, row in rows.items():
            original = archive.read(name)
            assert len(original) == row["bytes"] and digest(original) == row["sha256"]
            canonical = original.replace(b"\r\n", b"\n")
            assert canonical != original and row["difference_is_crlf_only"] is True
            assert len(canonical) == row["canonical_git_blob_bytes"]
            assert digest(canonical) == row["canonical_git_blob_sha256"]
            result["full_song_lua/proxmox-pass4-2026-11-19/" + name] = (original, canonical)
    return result


def verify_evidence_item(item, data, recovery):
    if item["path"] in recovery:
        original, canonical = recovery[item["path"]]
        # The old index still names the exact original bytes, never a new hash.
        assert len(original) == item["bytes"] and digest(original) == item["sha256"], item["path"]
        assert data == original or data == canonical, item["path"]
        recovered = data == canonical
    else:
        assert len(data) == item["bytes"], item["path"]
        assert digest(data) == item["sha256"], item["path"]
        recovered = False
    assert len(data) < 50_000_000, item["path"]
    return recovered


def verify():
    evidence = json.loads((ROOT / "evidence-files.json").read_text(encoding="utf-8"))
    recovery = original_byte_recovery()
    canonical_copies = []
    for item in evidence:
        path = (REPOSITORY / item["path"]).resolve()
        assert path.is_relative_to(ROOT), item["path"]
        data = path.read_bytes()
        if verify_evidence_item(item, data, recovery):
            canonical_copies.append(item["path"])
    bundles = [
        ("native-validation/validated-capture-evidence.zip", "native-validation/validated-manifest.json", "embedded"),
        ("native-validation/clock-control-failed-exercise.zip", "native-validation/failed_exercise-manifest.json", "embedded"),
        ("pipeline-baselines/life-pipeline-evidence.zip", "pipeline-baselines/manifest.json", "embedded"),
        ("native-life-score/life-event-score-evidence.zip", "native-life-score/manifest.json", "embedded"),
        ("native-life-score-glx/life-event-score-glx-evidence.zip", "native-life-score-glx/manifest.json", "embedded"),
        ("repaired-native-controls/replay-evidence.zip", "repaired-native-controls/manifest.json", "embedded"),
        ("negative-native-evidence/negative-evidence.zip", "negative-native-evidence/manifest.json", "verification"),
        ("played-stage-native/played-stage-native-evidence.zip", "played-stage-native/manifest.json", "external"),
        ("stream-finalization/stream-commit-b2af4f3.zip", "stream-finalization/manifest.json", "embedded"),
        ('final-addendum/portable-evidence-original-bytes/evidence.zip', 'final-addendum/portable-evidence-original-bytes/manifest.json', 'embedded'),
        ('final-addendum/candidate-b-build/candidate-evidence.zip', 'final-addendum/candidate-b-build/candidate-evidence-manifest.json', 'external'),
        ('final-addendum/candidate-b-build/provenance.zip', 'final-addendum/candidate-b-build/provenance-manifest.json', 'embedded'),
        ('final-addendum/windows-portable-visuals/evidence.zip', 'final-addendum/windows-portable-visuals/manifest.json', 'embedded'),
        ('final-addendum/cold-b-native/evidence.zip', 'final-addendum/cold-b-native/manifest.json', 'embedded'),
        ('final-addendum/stream-b-native/evidence.zip', 'final-addendum/stream-b-native/manifest.json', 'embedded'),
        ('final-addendum/circles-baseline-diagnosis/evidence.zip', 'final-addendum/circles-baseline-diagnosis/manifest.json', 'embedded'),
        ('final-addendum/quarantine-one-attempt/evidence.zip', 'final-addendum/quarantine-one-attempt/manifest.json', 'embedded'),
        ('final-addendum/missing-stage-primary-proof/evidence.zip', 'final-addendum/missing-stage-primary-proof/manifest.json', 'embedded'),
        ('final-addendum/retry-planning-and-authority/evidence.zip', 'final-addendum/retry-planning-and-authority/manifest.json', 'embedded'),
        ('final-addendum/stream-profile-package/evidence.zip', 'final-addendum/stream-profile-package/manifest.json', 'embedded'),
        ('final-addendum/rollout-point-in-time/evidence.zip', 'final-addendum/rollout-point-in-time/manifest.json', 'embedded'),
        ('final-addendum/commit-map-checkpoint/evidence.zip', 'final-addendum/commit-map-checkpoint/manifest.json', 'embedded'),
        ('final-addendum/post-cutoff-rollout-and-b-results/evidence.zip', 'final-addendum/post-cutoff-rollout-and-b-results/manifest.json', 'embedded'),
        ('final-addendum/preparation-provenance/evidence.zip', 'final-addendum/preparation-provenance/manifest.json', 'embedded'),
    ]
    counts = {}
    for archive_name, manifest_name, layout in bundles:
        embedded_manifest = layout == "embedded"
        manifest_bytes = (ROOT / manifest_name).read_bytes()
        manifest = json.loads(manifest_bytes)
        if not embedded_manifest:
            archive_bytes = (ROOT / archive_name).read_bytes()
            assert len(archive_bytes) == manifest["archive"]["bytes"], archive_name
            assert digest(archive_bytes) == manifest["archive"]["sha256"], archive_name
        members = manifest["members"] if layout == "external" else manifest["files"]
        member_key = "archive_path" if layout == "external" else "path"
        if isinstance(members, list):
            indexed = {item[member_key]: item for item in members}
            assert len(indexed) == len(members), "duplicate manifest members"
            members = indexed
        with zipfile.ZipFile(ROOT / archive_name) as archive:
            names = archive.namelist()
            assert len(names) == len(set(names)), "duplicate ZIP members"
            expected_names = set(members) | ({"manifest.json"} if embedded_manifest else set())
            assert set(names) == expected_names, (archive_name, set(names) ^ expected_names)
            if embedded_manifest:
                assert archive.read("manifest.json") == manifest_bytes, archive_name
            elif layout == "verification":
                assert json.loads(archive.read("verification.json")) == manifest["verification"], archive_name
            else:
                assert layout == "external", layout
            for name, expected in members.items():
                data = archive.read(name)
                assert len(data) == expected["bytes"], name
                assert digest(data) == expected["sha256"], name
        counts[archive_name] = len(names)
    print(json.dumps({"verified_files": len(evidence), "verified_zip_members": counts, "canonical_git_evidence_copies_verified": sorted(canonical_copies), "opaque_original_evidence_verified": len(recovery)}, sort_keys=True))


if __name__ == "__main__":
    verify()
