"""Apply one reviewed three-field snapshot migration; never harvest test output."""
import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
PROPOSAL = HERE / 'bitmap-zoom-migration-proposal'
RELATIVE = 'regression-expectations/deadsync-song-lua/a9485a8eaeb14743.snap'
ANCESTOR = '0a49b80d8dd1cbc59d86ac764e739537fcc1a79b'
BEFORE = 'dd009b84b7c3df4ba59e1e2fbb14f708b840ee84787bb62ad970c9562d9f49e0'
AFTER = 'ae9de3ca4b6a094b506ae6d36577303a056568e8a50dc790810aa87fa307949f'
PROPOSAL_SHA = 'dc0ea95c04de8822c2f2f876f423eb6e896e3ef829ebdb912b9f2cdea39437de'
AUTHORITIES = {
    'crates/deadsync-song-lua/src/actors/initial_state.rs': 'e741e2960bcbcf39cb992151449bb9e0048f8064b17cee4848a9e979343621f8',
    'crates/deadsync-song-lua/src/actors/draw.rs': 'be379bec4befbb97025124bc4334fc13586f3081150999c8e76dcfe97684ca6a',
}


def sha(data): return hashlib.sha256(data).hexdigest()
def git(repo, *args): return subprocess.check_output(['git', '-C', str(repo), *args])
def write_json(path, data):
    encoded = (json.dumps(data, indent=2) + '\n').encode()
    temporary = path.with_name(path.name + '.next')
    with temporary.open('xb') as stream:
        stream.write(encoded); stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)


def validate(args):
    assert re.fullmatch('[0-9a-f]{40}', args.expected_fixture_head), 'full explicit fixture revision required'
    fixture_repo = args.fixture_repo.resolve(strict=True)
    top = pathlib.Path(git(fixture_repo, 'rev-parse', '--show-toplevel').decode().strip()).resolve(strict=True)
    assert fixture_repo == top, 'fixture repo must be its Git root'
    head = git(fixture_repo, 'rev-parse', 'HEAD').decode().strip()
    assert head == args.expected_fixture_head, 'fixture HEAD differs'
    subprocess.run(['git', '-C', str(fixture_repo), 'merge-base', '--is-ancestor', ANCESTOR, head], check=True)
    status = git(fixture_repo, 'status', '--porcelain=v1', '--untracked-files=normal')
    assert not status, 'fixture worktree must be clean, including untracked additions'
    git(fixture_repo, 'ls-files', '--error-unmatch', '--', RELATIVE)
    path = fixture_repo / RELATIVE
    assert not path.is_symlink() and path.resolve(strict=True).is_relative_to(fixture_repo)
    before = path.read_bytes()
    assert sha(before) == BEFORE and len(before) == 12656, 'snapshot is not the reviewed original bytes'
    proposed = (PROPOSAL / 'a9485a8eaeb14743.proposed.snap').read_bytes()
    assert sha(proposed) == AFTER and len(proposed) == 12654, 'proposed bytes differ'
    proposal_bytes = (PROPOSAL / 'proposal.json').read_bytes()
    assert sha(proposal_bytes) == PROPOSAL_SHA
    proposal = json.loads(proposal_bytes)
    lines = before.splitlines(keepends=True)
    expected = lines.copy()
    assert len(lines) == 5 and lines[0].rstrip() == b'song/tests/rust_bitmap_text.rs::draw_frames'
    assert lines[1].rstrip() == b'test: retained_text_updates_during_live_tweens_and_draw_callbacks'
    for index, value in enumerate([b'1.25', b'1.75', b'2.0'], start=2):
        old = b', zoom: ' + value + b', zoom_x: ' + value + b', zoom_y: ' + value + b', zoom_z: ' + value + b','
        new = b', zoom: 1.0, zoom_x: ' + value + b', zoom_y: ' + value + b', zoom_z: ' + value + b','
        assert lines[index].count(old) == 1
        expected[index] = lines[index].replace(old, new, 1)
    assert b''.join(expected) == proposed, 'changes exceed the exact three-row allowlist'
    sources = []
    for relative, digest in AUTHORITIES.items():
        current = (REPO / relative).read_bytes().replace(b'\r\n', b'\n')
        assert sha(current) == digest, f'live source authority changed: {relative}'
        retained = PROPOSAL / 'source-authorities' / pathlib.Path(relative).name
        assert sha(retained.read_bytes()) == digest
        sources.append({'path': relative, 'normalized_sha256': digest})
    for row in proposal['failing_logs']:
        assert sha(pathlib.Path(row['path']).read_bytes()) == row['sha256']
    return fixture_repo, path, before, proposed, proposal, sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected-fixture-head', required=True)
    parser.add_argument('--fixture-repo', type=pathlib.Path, default=REPO / 'tests/fixtures')
    parser.add_argument('--apply', action='store_true', help='perform only the reviewed snapshot replacement; default verifies without writes')
    args = parser.parse_args()
    fixture_repo, path, before, proposed, proposal, sources = validate(args)
    if not args.apply:
        print(json.dumps({'ready': True, 'applied': False, 'fixture_head': args.expected_fixture_head,
                          'before_sha256': BEFORE, 'proposed_sha256': AFTER, 'allowed_rows': [3, 4, 5]}))
        return
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    output = HERE / 'bitmap-zoom-migration-applied' / stamp
    output.mkdir(parents=True)
    (output / 'before.snap').write_bytes(before)
    (output / 'proposed.snap').write_bytes(proposed)
    shutil.copyfile(PROPOSAL / 'proposal.json', output / 'proposal.json')
    for row in proposal['failing_logs']:
        shutil.copyfile(row['path'], output / pathlib.Path(row['path']).name)
    receipt = {'schema_version': 1, 'state': 'prepared', 'started_at': dt.datetime.now(dt.timezone.utc).isoformat(),
               'fixture_repo': str(fixture_repo), 'expected_fixture_head': args.expected_fixture_head,
               'path': RELATIVE, 'before_sha256': BEFORE, 'proposed_sha256': AFTER,
               'changes': proposal['changes'], 'proposal_sha256': PROPOSAL_SHA,
               'source_authorities': sources, 'script_sha256': sha(pathlib.Path(__file__).read_bytes()),
               'tests_executed': False, 'native_parity_claim': False, 'committed': False}
    write_json(output / 'receipt.json', receipt)
    # Recheck after preserving evidence; no checkout, reset, clean or unrelated file writes.
    validate(args)
    temporary = path.with_name(path.name + '.bitmap-zoom-' + stamp + '.tmp')
    with temporary.open('xb') as stream:
        stream.write(proposed); stream.flush(); os.fsync(stream.fileno())
    assert path.read_bytes() == before, 'snapshot changed before replace; owned temporary preserved'
    os.replace(temporary, path)
    assert sha(path.read_bytes()) == AFTER
    status = git(fixture_repo, 'status', '--porcelain=v1', '--untracked-files=normal').decode().splitlines()
    assert status == [' M ' + RELATIVE], 'unexpected concurrent fixture changes; evidence and applied snapshot preserved'
    receipt.update(state='applied-awaiting-validation', finished_at=dt.datetime.now(dt.timezone.utc).isoformat(),
                   applied_sha256=sha(path.read_bytes()), exact_three_field_changes=True, fixture_status=status)
    write_json(output / 'receipt.json', receipt)
    print(json.dumps({'receipt': str(output / 'receipt.json'), 'receipt_sha256': sha((output / 'receipt.json').read_bytes()),
                      'applied_sha256': AFTER, 'tests_executed': False, 'native_parity_claim': False}, indent=2))


if __name__ == '__main__': main()
