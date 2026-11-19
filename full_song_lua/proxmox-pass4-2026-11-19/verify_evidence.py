"""Verify the exact native evidence checkpoint without extracting ZIP members."""
import hashlib
import json
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parent
REPOSITORY = ROOT.parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify():
    evidence = json.loads((ROOT / "evidence-files.json").read_text(encoding="utf-8"))
    for item in evidence:
        path = (REPOSITORY / item["path"]).resolve()
        assert path.is_relative_to(ROOT), item["path"]
        data = path.read_bytes()
        assert len(data) == item["bytes"], item["path"]
        assert digest(data) == item["sha256"], item["path"]
        assert len(data) < 50_000_000, item["path"]
    bundles = [
        ("native-validation/validated-capture-evidence.zip", "native-validation/validated-manifest.json"),
        ("native-validation/clock-control-failed-exercise.zip", "native-validation/failed_exercise-manifest.json"),
        ("pipeline-baselines/life-pipeline-evidence.zip", "pipeline-baselines/manifest.json"),
        ("native-life-score/life-event-score-evidence.zip", "native-life-score/manifest.json"),
    ]
    counts = {}
    for archive_name, manifest_name in bundles:
        manifest_bytes = (ROOT / manifest_name).read_bytes()
        manifest = json.loads(manifest_bytes)
        members = manifest["files"]
        if isinstance(members, list):
            indexed = {item["path"]: item for item in members}
            assert len(indexed) == len(members), "duplicate manifest members"
            members = indexed
        with zipfile.ZipFile(ROOT / archive_name) as archive:
            names = archive.namelist()
            assert len(names) == len(set(names)), "duplicate ZIP members"
            expected_names = set(members) | {"manifest.json"}
            assert set(names) == expected_names, (archive_name, set(names) ^ expected_names)
            assert archive.read("manifest.json") == manifest_bytes, archive_name
            for name, expected in members.items():
                data = archive.read(name)
                assert len(data) == expected["bytes"], name
                assert digest(data) == expected["sha256"], name
        counts[archive_name] = len(names)
    print(json.dumps({"verified_files": len(evidence), "verified_zip_members": counts}, sort_keys=True))


if __name__ == "__main__":
    verify()
