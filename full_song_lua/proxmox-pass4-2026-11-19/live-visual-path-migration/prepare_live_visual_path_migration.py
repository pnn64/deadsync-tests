"""Apply the approved exact path-token proposal and retain bounded evidence."""
import collections
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess

TASK = Path(__file__).resolve().parent
PRODUCT = TASK.parents[1]
FIXTURES = Path("C:/GitHub/deadsync-fixtures-lua-fleet-20261119")
PROPOSAL = TASK / "live-visual-path-registration-proposal-20261119T045514.571696Z"
HEAD = "21f47c8783a1fe429a8a5f341ca604d03773601c"
FIXTURE_HEAD = "d2aa6cfef449e13fd92b7a7264659dec3cb31fdc"
PROPOSAL_SHA = "8e65f94804d34d121a39d07773a6f04d4c570f16f743b5e9621ecbac1cd4ba8c"
SOURCE = "crates/deadsync-song-lua/tests/live_visuals.rs"
PREFIX = Path("full_song_lua/proxmox-pass4-2026-11-19")
EVIDENCE = FIXTURES / PREFIX
MIGRATION = EVIDENCE / "live-visual-path-migration"
FONT = EVIDENCE / "font-file-alias"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


def head(root):
    return git(root, "rev-parse", "HEAD").decode().strip()


def record(path, relative_to=None):
    data = path.read_bytes()
    return {"path": str(path.relative_to(relative_to)).replace("\\", "/") if relative_to else str(path),
            "bytes": len(data), "sha256": sha(data)}


def write_json(path, value):
    path.write_bytes((json.dumps(value, indent=2) + "\n").encode())


def main():
    assert head(PRODUCT) == HEAD and head(FIXTURES) == FIXTURE_HEAD
    assert head(PRODUCT / "tests/fixtures") == FIXTURE_HEAD
    for repo in [PRODUCT, FIXTURES, PRODUCT / "tests/fixtures"]:
        assert not git(repo, "status", "--porcelain=v1", "--untracked-files=all").strip(), str(repo)
        assert not git(repo, "diff", "--cached", "--binary").strip(), str(repo)
    assert not MIGRATION.exists()
    proposal_bytes = (PROPOSAL / "proposal.json").read_bytes()
    assert sha(proposal_bytes) == PROPOSAL_SHA
    proposal = json.loads(proposal_bytes)
    assert proposal["product_head"] == HEAD and proposal["fixture_head"] == FIXTURE_HEAD
    before_source = (PROPOSAL / "original/live_visuals.rs").read_bytes()
    after_source = (PROPOSAL / "proposed/live_visuals.rs").read_bytes()
    assert (PRODUCT / SOURCE).read_bytes() == before_source
    assert sha(before_source) == proposal["source"]["before_sha256"] == "883d52719246b62040bac23f8c001b38644d5914f0ee6268cfc99ece92a15bbd"
    assert sha(after_source) == proposal["source"]["proposed_sha256"] == "a1c8fc5150d8cc56b1e9956fe63be8f276d53f090b9624f27a0a03149631012a"
    assert sha((PROPOSAL / "source.patch").read_bytes()) == proposal["source_patch_sha256"] == "155332c86183b3be455589220ec99713294455b0468be344e1260bf55f26b963"
    authority = PRODUCT / "crates/deadlib-lua/src/reference_test.rs"
    assert authority.read_bytes() == (PROPOSAL / "reference_test.rs").read_bytes()
    assert sha(authority.read_bytes()) == proposal["authority"]["sha256"]
    nl = b"\r\n" if b"\r\n" in before_source else b"\n"
    old = nl.join([b"        reference_test::register_path(dir.path());",
                   b'        let path = dir.path().join("default.lua");'])
    new = nl.join([b'        let path = dir.path().join("default.lua");',
                   b"        // Exact files precede their directory so its prefix cannot consume",
                   b"        // their portable snapshot tokens.",
                   b"        reference_test::register_path(&path);",
                   b'        reference_test::register_path(&dir.path().join("art.png"));',
                   b'        reference_test::register_path(&dir.path().join("second.png"));',
                   b"        reference_test::register_path(dir.path());"])
    assert before_source.count(old) == 1 and before_source.replace(old, new, 1) == after_source
    replacements = {b'"$FIXTURE0\\\\default.lua"': b'"$FIXTURE0"',
                    b'"$FIXTURE0\\\\art.png"': b'"$FIXTURE1"',
                    b'"$FIXTURE0\\\\second.png"': b'"$FIXTURE2"'}
    pattern = re.compile(b"|".join(re.escape(x) for x in replacements))
    expected_names = {"b3216bc62d36e29c.snap", "be88a6d727933ed4.snap", "28e74d92d026cc0b.snap"}
    assert {Path(x["path"]).name for x in proposal["snapshots"]} == expected_names
    validated = []
    total_count = total_rows = 0
    for item in proposal["snapshots"]:
        rel = item["path"]
        assert rel == "regression-expectations/deadsync-song-lua/" + Path(rel).name
        before = (PROPOSAL / "original" / Path(rel).name).read_bytes()
        after = (PROPOSAL / "proposed" / Path(rel).name).read_bytes()
        assert len(before) == item["before_bytes"] and sha(before) == item["before_sha256"]
        assert len(after) == item["proposed_bytes"] and sha(after) == item["proposed_sha256"]
        assert git(FIXTURES, "show", f"{FIXTURE_HEAD}:{rel}") == before
        target = FIXTURES / rel
        if target.exists():
            assert target.read_bytes() == before
        expected = pattern.sub(lambda m: replacements[m.group()], before)
        assert expected == after
        matches = list(pattern.finditer(before))
        assert {m.start() for m in re.finditer(rb"\$FIXTURE\d+", before)} == {m.start()+1 for m in matches}
        assert dict(collections.Counter(m.group().decode() for m in matches)) == item["replacement_counts"]
        rows = []
        for line, (a, b) in enumerate(zip(before.splitlines(keepends=True), after.splitlines(keepends=True)), 1):
            assert b == pattern.sub(lambda m: replacements[m.group()], a)
            if a != b:
                rows.append((line, sha(a), sha(b)))
        assert len(before.splitlines()) == len(after.splitlines())
        assert [(x["line"], x["before_sha256"], x["after_sha256"]) for x in item["changed_rows"]] == rows
        assert before.count(b"\r\n") == after.count(b"\r\n")
        assert before.count(b"\n") == after.count(b"\n")
        total_count += len(matches)
        total_rows += len(rows)
        validated.append((item, before, after, git(FIXTURES, "ls-files", "-v", "--", rel).decode().strip(), target.exists()))
    assert (total_count, total_rows) == (406, 63)
    attrs_before = (FIXTURES / ".gitattributes").read_bytes()
    attrs_after = (PROPOSAL / "proposed/.gitattributes").read_bytes()
    assert attrs_before == (PROPOSAL / "original/.gitattributes").read_bytes()
    assert sha(attrs_before) == "3596e8e8ecfb3d54efd56178a69f861b83d5f0195dabea01d372a05c4560bd81"
    assert sha(attrs_after) == "938dda7015bbdd6b15df508b59159db0ea9047d70152a4bf82b21a9c72519599"
    proof_bytes = (PROPOSAL / "whitespace-annotation-proof.json").read_bytes()
    assert sha(proof_bytes) == "0c4c4ea94d5a58db3f54c4d9c148ef14142d818c51aba9470cba74b995b51af1"
    proof = json.loads(proof_bytes)
    assert [x for x in attrs_after.splitlines() if x not in attrs_before.splitlines()] == [x.encode() for x in proof["only_added_attribute_lines"]]
    gate = TASK / "corpus-audit-history-controls-20261119T044549Z"
    gate_bytes = (gate / "receipt.json").read_bytes()
    assert sha(gate_bytes) == "bd089e41afe151edd16324c13d952ac823fff15db9e7cfd2e0f325c8680b2569"
    gate_receipt = json.loads(gate_bytes)
    assert [x["name"] for x in gate_receipt["commands"]] == ["diff-check", "bitmap-text", "live-visuals", "live-gameplay"]
    for command in gate_receipt["commands"]:
        assert command["exit_code"] == 0 and command["source_unchanged"] is True
        assert command["source_before"] == command["source_after"]
        assert sha(Path(command["log"]).read_bytes()) == command["log_sha256"]
    commit_receipt = json.loads((TASK / "font-resolution-commit.json").read_bytes())
    assert commit_receipt["commit"] == HEAD and commit_receipt["windows_gate_receipt_sha256"] == sha(gate_bytes)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    out = TASK / ("live-visual-path-migration-preparation-" + stamp)
    out.mkdir()
    manifest_path = EVIDENCE / "evidence-files.json"
    manifest_before = manifest_path.read_bytes()
    manifest = json.loads(manifest_before)
    readme_path = EVIDENCE / "README.md"
    readme_before = readme_path.read_bytes()
    (out / "evidence-files.before.json").write_bytes(manifest_before)
    (out / "README.before.md").write_bytes(readme_before)
    print(json.dumps({"phase": "preflight_passed", "directory": str(out), "replacements": total_count, "rows": total_rows}), flush=True)
    # Only exact approved targets are changed after all source/snapshot checks.
    (PRODUCT / SOURCE).write_bytes(after_source)
    materialized = []
    for item, before, after, flags, exists in validated:
        target = FIXTURES / item["path"]
        if not exists:
            git(FIXTURES, "update-index", "--no-skip-worktree", "--", item["path"])
            target.parent.mkdir(parents=True, exist_ok=True)
            materialized.append({"path": item["path"], "prior_index_flag": flags})
        target.write_bytes(after)
        assert target.read_bytes() == after
    pre = subprocess.run(["git", "-C", str(FIXTURES), "diff", "--check"], capture_output=True)
    (out / "diff-check-before-annotations.stdout").write_bytes(pre.stdout)
    (out / "diff-check-before-annotations.stderr").write_bytes(pre.stderr)
    annotations_applied = False
    if pre.returncode:
        warnings = re.findall(rb"(?m)^([^\r\n]+):(\d+): trailing whitespace\.\r?$", pre.stdout)
        expected_warnings = {(item["path"], row["line"]) for item in proposal["snapshots"] for row in item["changed_rows"]}
        assert pre.returncode == 2 and not pre.stderr
        assert {(p.decode(), int(n)) for p, n in warnings} == expected_warnings and len(warnings) == 63
        (FIXTURES / ".gitattributes").write_bytes(attrs_after)
        annotations_applied = True
    post = subprocess.run(["git", "-C", str(FIXTURES), "diff", "--check"], capture_output=True)
    (out / "diff-check-after-annotations.stdout").write_bytes(post.stdout)
    (out / "diff-check-after-annotations.stderr").write_bytes(post.stderr)
    assert post.returncode == 0 and not post.stdout and not post.stderr
    copied = []
    def retain(src, dest):
        data = src.read_bytes()
        assert len(data) < 50_000_000 and not dest.exists(), str(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        assert dest.read_bytes() == data
        copied.append(record(dest, FIXTURES))
    for rel in ["proposal.json", "source.patch", "reference_test.rs", "whitespace-annotation-proof.json",
                "original/live_visuals.rs", "proposed/live_visuals.rs",
                "original/.gitattributes", "proposed/.gitattributes"]:
        retain(PROPOSAL / rel, MIGRATION / rel)
    for name in sorted(expected_names):
        for state in ["original", "proposed"]:
            retain(PROPOSAL / state / name, MIGRATION / state / name)
    for label in ["before", "after"]:
        for stream in ["stdout", "stderr"]:
            name = f"diff-check-{label}-annotations.{stream}"
            retain(PROPOSAL / name, MIGRATION / "annotation-control" / name)
            # Identical real-repository outputs reuse the verbatim proof log.
            if (out / name).read_bytes() != (PROPOSAL / name).read_bytes():
                retain(out / name, MIGRATION / "application" / name)
    for name in ["propose_live_visual_path_registration.py",
                 "independent-full24-path-suffix-audit.json",
                 "independent-full24-encoded-path-audit.json"]:
        retain(TASK / name, MIGRATION / name)
    retain(Path(__file__), MIGRATION / Path(__file__).name)
    gate_files = sorted(x for x in gate.iterdir() if x.is_file())
    assert len(gate_files) == 21
    for path in gate_files:
        retain(path, FONT / "windows-controls-20261119T044549Z" / path.name)
    for name in ["font-resolution-commit.json", "commit_font_resolution_fix.py"]:
        retain(TASK / name, FONT / name)
    application = {
        "status": "approved exact application verified; final verifier receipt retained separately",
        "product_head": HEAD, "product_fixture_head_unchanged": FIXTURE_HEAD,
        "separate_fixture_parent": FIXTURE_HEAD, "proposal_sha256": PROPOSAL_SHA,
        "source": record(PRODUCT / SOURCE, PRODUCT),
        "snapshot_replacements": total_count, "changed_snapshot_rows": total_rows,
        "only_exact_quoted_path_tokens_changed": True, "all_other_snapshot_bytes_and_crlf_preserved": True,
        "materialized_exact_paths": materialized,
        "snapshots": [record(FIXTURES / item["path"], FIXTURES) for item in proposal["snapshots"]],
        "annotations_applied_after_actual_diff_check": annotations_applied,
        "actual_diff_checks": {
            "before": {"exit_code": pre.returncode, "stdout_sha256": sha(pre.stdout), "stderr_sha256": sha(pre.stderr)},
            "after": {"exit_code": post.returncode, "stdout_sha256": sha(post.stdout), "stderr_sha256": sha(post.stderr)}},
        "attributes": record(FIXTURES / ".gitattributes", FIXTURES),
        "global_normalizer_sha256_unchanged": sha(authority.read_bytes()),
        "runtime_changed": False, "cargo_executed": False, "product_index_changed": False,
        "product_fixture_checkout_changed": False,
        "pending": ["publish fixture commit", "full Windows live_visuals and diff-check against published fixtures", "Linux candidate B gates"],
        "retained_font_gate_receipt_sha256": sha(gate_bytes),
        "retained_font_gate_counts": {"bitmap_text": 11, "live_visuals": 13, "live_gameplay": 17},
    }
    write_json(out / "application.json", application)
    retain(out / "application.json", MIGRATION / "application.json")
    addition = (
        "\n\n## Portable live-visual paths and completed font gates\n\n"
        "live-visual-path-migration/ preserves the reviewed test-only registration\n"
        "of the three known input files before their directory. Distinct tokens\n"
        "retain default.lua, art.png and second.png identity on both platforms.\n"
        "Exactly 406 quoted path substitutions affect 63 rows in three snapshots;\n"
        "all other snapshot bytes and CRLF endings are unchanged. Source-derived\n"
        "before/after files, the complete 24-snapshot audit, and exact application\n"
        "and whitespace-annotation proofs are retained. Runtime paths and the global\n"
        "normalizer are unchanged. The post-publication Windows live_visuals gate\n"
        "and Linux candidate B gates remain pending at this preparation checkpoint.\n\n"
        "font-file-alias/windows-controls-20261119T044549Z/ retains every original\n"
        "log, receipt and before/after patch from the completed Windows font gate.\n"
        "BitmapText passed 11 tests, live_visuals 13 and live_gameplay 17, with no\n"
        "failed or ignored tests. Source and fixtures remained unchanged throughout:\n"
        "DeadSync 4224b3b2eb5dbc0efd15618bf86266bb651af56c plus patch SHA-256\n"
        "dae16a7955e018030beef96ff69fcc8527a5f3cf06a30c598e2c8e3dd302aecf,\n"
        "using clean fixture d2aa6cfef449e13fd92b7a7264659dec3cb31fdc. The exact\n"
        "reviewed font subset was committed as 21f47c8783a1fe429a8a5f341ca604d03773601c;\n"
        "its original commit receipt and helper are retained. These completed gates\n"
        "precede the separate live-visual path registration change and do not claim\n"
        "Linux or complete fleet parity.\n"
    ).encode()
    readme_nl = b"\r\n" if b"\r\n" in readme_before else b"\n"
    readme_path.write_bytes(readme_before + addition.replace(b"\n", readme_nl))
    assert readme_path.read_bytes().startswith(readme_before)
    existing_paths = {x["path"] for x in manifest}
    assert len(existing_paths) == len(manifest)
    assert not existing_paths.intersection(x["path"] for x in copied)
    assert len({x["path"] for x in copied}) == len(copied)
    manifest_nl = b"\r\n"
    closing = manifest_nl + b"]" + manifest_nl
    assert manifest_before.endswith(closing) and manifest_before.count(b"\r\n") == manifest_before.count(b"\n")
    inner = manifest_nl.join(line.encode() for line in json.dumps(copied, indent=2).splitlines()[1:-1])
    manifest_after = manifest_before[:-len(closing)] + b"," + manifest_nl + inner + closing
    assert json.loads(manifest_after) == manifest + copied
    assert manifest_after.startswith(manifest_before[:-len(closing)])
    manifest_path.write_bytes(manifest_after)
    assert (PRODUCT / SOURCE).read_bytes() == after_source
    assert sha(authority.read_bytes()) == proposal["authority"]["sha256"]
    assert head(PRODUCT) == HEAD and head(PRODUCT / "tests/fixtures") == FIXTURE_HEAD
    assert not git(PRODUCT / "tests/fixtures", "status", "--porcelain=v1").strip()
    assert git(PRODUCT, "diff", "--name-only").decode().splitlines() == [SOURCE]
    assert not git(PRODUCT, "diff", "--cached", "--binary").strip()
    assert not git(FIXTURES, "diff", "--cached", "--binary").strip()
    patch = git(PRODUCT, "diff", "--binary", "--full-index", "HEAD")
    (out / "product-source.patch").write_bytes(patch)
    checks = {}
    for name, command, cwd in [
        ("fixture-verifier", ["python", "-X", "utf8", str(EVIDENCE / "verify_evidence.py")], FIXTURES),
        ("fixture-diff-check", ["git", "diff", "--check"], FIXTURES),
        ("product-diff-check", ["git", "diff", "--check"], PRODUCT),
    ]:
        result = subprocess.run(command, cwd=cwd, capture_output=True)
        (out / f"{name}.stdout").write_bytes(result.stdout)
        (out / f"{name}.stderr").write_bytes(result.stderr)
        checks[name] = {"command": command, "exit_code": result.returncode,
                       "stdout_sha256": sha(result.stdout), "stderr_sha256": sha(result.stderr)}
        assert result.returncode == 0, (name, result.returncode, str(out))
    changed = git(FIXTURES, "diff", "--name-only").decode().splitlines()
    expected_changed = {".gitattributes", str(PREFIX / "README.md").replace("\\", "/"),
                        str(PREFIX / "evidence-files.json").replace("\\", "/")} | {x["path"] for x in proposal["snapshots"]}
    if not annotations_applied:
        expected_changed.remove(".gitattributes")
    assert set(changed) == expected_changed
    untracked = git(FIXTURES, "ls-files", "--others", "--exclude-standard", "-z").decode().strip("\0").split("\0")
    assert set(untracked) == {x["path"] for x in copied}
    handoff = {
        "status": "prepared and verified; not committed, pushed, or checked out in product",
        "directory": str(out), "product_head": HEAD, "product_source_patch_sha256": sha(patch),
        "product_source": record(PRODUCT / SOURCE, PRODUCT),
        "fixture_parent": FIXTURE_HEAD, "fixture_manifest": record(manifest_path, FIXTURES),
        "verifier": record(EVIDENCE / "verify_evidence.py", FIXTURES),
        "modified": [record(FIXTURES / name, FIXTURES) for name in changed],
        "added": copied, "added_files": len(copied), "added_bytes": sum(x["bytes"] for x in copied),
        "checks": checks, "evidence_verification": json.loads((out / "fixture-verifier.stdout").read_bytes()),
        "product_fixture_checkout_unchanged": True, "product_index_unchanged": True,
        "fixture_staging_unchanged": True, "runtime_unchanged": True, "cargo_executed": False,
    }
    write_json(out / "handoff.json", handoff)
    print(json.dumps({"phase": "complete", "handoff": str(out / "handoff.json"),
                      "handoff_sha256": sha((out / "handoff.json").read_bytes()),
                      "modified_files": len(changed), "added_files": len(copied),
                      "added_bytes": handoff["added_bytes"], "manifest_sha256": sha(manifest_after),
                      "source_patch_sha256": sha(patch), "evidence_verification": handoff["evidence_verification"]}), flush=True)


if __name__ == "__main__":
    main()
