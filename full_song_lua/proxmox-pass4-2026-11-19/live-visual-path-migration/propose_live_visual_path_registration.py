"""Prepare exact test-registration/snapshot token proposals without applying them."""
import collections
import datetime
import difflib
import hashlib
import json
import pathlib
import re
import subprocess

WORK = pathlib.Path(__file__).resolve().parent
REPO = WORK.parents[1]
FIXTURES = REPO / 'tests/fixtures'
EXPECTED_HEAD = '21f47c8783a1fe429a8a5f341ca604d03773601c'
FIXTURE_HEAD = 'd2aa6cfef449e13fd92b7a7264659dec3cb31fdc'
SNAPSHOTS = ['b3216bc62d36e29c.snap', 'be88a6d727933ed4.snap', '28e74d92d026cc0b.snap']


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    assert git(REPO, 'rev-parse', 'HEAD').decode().strip() == EXPECTED_HEAD
    assert not git(REPO, 'status', '--porcelain', '--untracked-files=all').strip()
    assert git(FIXTURES, 'rev-parse', 'HEAD').decode().strip() == FIXTURE_HEAD
    assert not git(FIXTURES, 'status', '--porcelain', '--untracked-files=all').strip()
    source_path = REPO / 'crates/deadsync-song-lua/tests/live_visuals.rs'
    source = source_path.read_bytes()
    newline = b'\r\n' if b'\r\n' in source else b'\n'
    before = newline.join([b'        reference_test::register_path(dir.path());',
                           b'        let path = dir.path().join("default.lua");'])
    after = newline.join([b'        let path = dir.path().join("default.lua");',
        b'        // Exact files precede their directory so its prefix cannot consume',
        b'        // their portable snapshot tokens.',
        b'        reference_test::register_path(&path);',
        b'        reference_test::register_path(&dir.path().join("art.png"));',
        b'        reference_test::register_path(&dir.path().join("second.png"));',
        b'        reference_test::register_path(dir.path());'])
    assert source.count(before) == 1
    proposed_source = source.replace(before, after, 1)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    output = WORK / ('live-visual-path-registration-proposal-' + stamp)
    (output / 'original').mkdir(parents=True); (output / 'proposed').mkdir()
    (output / 'original/live_visuals.rs').write_bytes(source)
    (output / 'proposed/live_visuals.rs').write_bytes(proposed_source)
    patch = ''.join(difflib.unified_diff(source.decode().replace('\r\n', '\n').splitlines(keepends=True),
        proposed_source.decode().replace('\r\n', '\n').splitlines(keepends=True),
        fromfile='a/crates/deadsync-song-lua/tests/live_visuals.rs',
        tofile='b/crates/deadsync-song-lua/tests/live_visuals.rs')).encode()
    (output / 'source.patch').write_bytes(patch)
    authority = REPO / 'crates/deadlib-lua/src/reference_test.rs'
    (output / 'reference_test.rs').write_bytes(authority.read_bytes())
    # The existing test registers exactly one directory per Pair and snapshots
    # contain only its $FIXTURE0. Full file registrations now get tokens 0/1/2;
    # the remaining directory gets token3. Use a single longest-first pass so
    # newly written tokens are never remapped by a subsequent replacement.
    replacements = {b'"$FIXTURE0"': b'"$FIXTURE3"'}
    token_map = {'default.lua': '$FIXTURE0', 'art.png': '$FIXTURE1', 'second.png': '$FIXTURE2'}
    for name, token in token_map.items():
        for separator in [b'\\\\', b'/']:
            replacements[b'"$FIXTURE0' + separator + name.encode() + b'"'] = b'"' + token.encode() + b'"'
    pattern = re.compile(b'|'.join(re.escape(value) for value in sorted(replacements, key=len, reverse=True)))
    records = []
    for name in SNAPSHOTS:
        relative = 'regression-expectations/deadsync-song-lua/' + name
        original = (FIXTURES / relative).read_bytes()
        assert set(re.findall(rb'\$FIXTURE[0-9]+', original)) == {b'$FIXTURE0'}
        matches = list(pattern.finditer(original))
        assert matches
        for match in matches:
            assert match.group() != b'"$FIXTURE0"', 'unexpected bare directory token needs review'
        covered = {match.start() + 1 for match in matches}
        assert {match.start() for match in re.finditer(rb'\$FIXTURE[0-9]+', original)} == covered
        replacement_counts = collections.Counter(match.group().decode() for match in matches)
        proposed = pattern.sub(lambda match: replacements[match.group()], original)
        old_lines = original.splitlines(keepends=True); new_lines = proposed.splitlines(keepends=True)
        assert len(old_lines) == len(new_lines)
        rows = []
        test = None
        for index, (old, new) in enumerate(zip(old_lines, new_lines), 1):
            if old.startswith(b'test: '): test = old[6:].strip().decode()
            assert new == pattern.sub(lambda match: replacements[match.group()], old)
            if old != new:
                rows.append({'line': index, 'test': test, 'before_bytes': len(old), 'after_bytes': len(new),
                             'before_sha256': digest(old), 'after_sha256': digest(new),
                             'replacements': dict(collections.Counter(match.group().decode() for match in pattern.finditer(old)))})
        assert original.count(b'\r\n') == proposed.count(b'\r\n')
        (output / 'original' / name).write_bytes(original)
        (output / 'proposed' / name).write_bytes(proposed)
        records.append({'path': relative, 'before_sha256': digest(original), 'before_bytes': len(original),
                        'proposed_sha256': digest(proposed), 'proposed_bytes': len(proposed),
                        'changed_rows': rows, 'replacement_counts': dict(replacement_counts),
                        'all_other_bytes_preserved': True})
    result = {'schema_version': 1, 'status': 'proposal only; not applied or executed',
              'product_head': EXPECTED_HEAD, 'fixture_head': FIXTURE_HEAD,
              'source': {'path': str(source_path), 'before_sha256': digest(source),
                         'proposed_sha256': digest(proposed_source), 'only_registration_order_and_entries_changed': True},
              'authority': {'path': str(authority), 'sha256': digest(authority.read_bytes()),
                            'register_path_lines': '36-57', 'ordered_replacement_lines': '60-72'},
              'token_map': {'exact_default_file': '$FIXTURE0', 'exact_art_file': '$FIXTURE1',
                            'exact_second_file': '$FIXTURE2', 'remaining_directory': '$FIXTURE3'},
              'registry_order': ['default.lua', 'art.png', 'second.png', 'directory'],
              'ordering_reason': 'normalize processes PATHS in insertion order, so complete file paths replace before their directory prefix; appending files after the directory would not work.',
              'path_binding': 'Register only independently known input paths. The exact Pair has no remapped foreground/background source; song_layers preserves its native source_path, loader keeps its native parent script_dir, and actor asset resolution joins the known filenames onto that directory. Existing registration adds each all-forward alias. No actual output path is adopted as an expectation.',
              'source_patch_sha256': digest(patch),
              'snapshots': records, 'runtime_or_global_normalizer_changes': False,
              'source_mutated': False, 'fixtures_mutated': False, 'cargo_executed': False}
    assert sum(sum(row['replacement_counts'].values()) for row in records) == 406
    assert sum(len(row['changed_rows']) for row in records) == 63
    assert source_path.read_bytes() == source
    assert git(REPO, 'rev-parse', 'HEAD').decode().strip() == EXPECTED_HEAD
    assert not git(REPO, 'status', '--porcelain', '--untracked-files=all').strip()
    raw = (json.dumps(result, indent=2) + '\n').encode(); (output / 'proposal.json').write_bytes(raw)
    print(json.dumps({'directory': str(output), 'proposal_sha256': digest(raw), 'source': result['source'],
                      'snapshots': [{key: row[key] for key in ['path', 'before_sha256', 'proposed_sha256', 'replacement_counts']} |
                                    {'changed_rows': len(row['changed_rows'])} for row in records]}))


if __name__ == '__main__':
    main()
