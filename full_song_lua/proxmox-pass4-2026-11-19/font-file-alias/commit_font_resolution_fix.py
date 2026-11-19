"""Commit only the exact font changes accepted by the final Windows gates."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[1]
HEAD = '4224b3b2eb5dbc0efd15618bf86266bb651af56c'
FIXTURE = 'd2aa6cfef449e13fd92b7a7264659dec3cb31fdc'
PATCH = 'dae16a7955e018030beef96ff69fcc8527a5f3cf06a30c598e2c8e3dd302aecf'
FILES = {
    'crates/deadsync-song-lua/src/actors/assets.rs': '6f2bd55942e9ba83ab4f55f19869037c3d31aad90499981085c11124b2acbbff',
    'crates/deadsync-song-lua/src/actors/text.rs': '53a58d1e534bf7676b424d098d43a82f0c233a5ffafc2d99da8461bfe471c648',
    'crates/deadsync-song-lua/tests/bitmap_text.rs': '201993bbaca56b7fc67142784f839df1185dda4a7cec1ac220f5d9704484d6f9',
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def git(*args, cwd=ROOT):
    return subprocess.check_output(['git', '-C', str(cwd), *args])

def main():
    receipt_path = Path(sys.argv[1]).resolve()
    assert receipt_path.is_relative_to(TASK) and receipt_path.name == 'receipt.json'
    receipt_bytes = receipt_path.read_bytes()
    receipt = json.loads(receipt_bytes)
    rows = receipt['commands']
    assert [row['name'] for row in rows] == ['diff-check', 'bitmap-text', 'live-visuals', 'live-gameplay']
    expected_source = {
        'source': {'head': HEAD, 'patch_sha256': PATCH},
        'fixtures': {'head': FIXTURE, 'patch_sha256': sha(b'')},
    }
    for row in rows:
        assert row['exit_code'] == 0 and row['source_unchanged'] is True
        assert row['source_before'] == row['source_after'] == expected_source
        log_path = Path(row['log']).resolve()
        assert log_path.parent == receipt_path.parent
        assert sha(log_path.read_bytes()) == row['log_sha256']
        if row['name'] != 'diff-check':
            assert len(row['result_lines']) == 1
            result = re.fullmatch(r'test result: ok\. (\d+) passed; 0 failed; .*', row['result_lines'][0])
            assert result and int(result[1]) > 0
    assert git('rev-parse', 'HEAD').decode().strip() == HEAD
    assert not git('diff', '--cached', '--name-only').strip()
    assert not git('ls-files', '--others', '--exclude-standard', '-z').strip(b'\0')
    assert git('rev-parse', 'HEAD', cwd=ROOT / 'tests/fixtures').decode().strip() == FIXTURE
    assert not git('status', '--porcelain=v1', cwd=ROOT / 'tests/fixtures').strip()
    patch = git('diff', '--binary', '--full-index', 'HEAD')
    assert sha(patch) == PATCH
    changed = set(git('diff', '--name-only', 'HEAD', '-z').decode().strip('\0').split('\0'))
    assert changed == set(FILES) | {'tests/fixtures'}
    for name, expected in FILES.items():
        assert sha((ROOT / name).read_bytes()) == expected, name
    git('diff', '--check')
    git('add', '--', *FILES, 'tests/fixtures')
    assert git('diff', '--cached', '--binary', '--full-index', 'HEAD') == patch
    git('diff', '--cached', '--check')
    subprocess.run(['git', '-C', str(ROOT), 'commit', '-m',
        'fix(song-lua): resolve legacy bitmap font files before theme aliases', '-m',
        'Match native Font/File path precedence, preserve cached caller path spelling, and assert physical font paths independently of portable snapshot presentation.'], check=True)
    commit = git('rev-parse', 'HEAD').decode().strip()
    assert git('rev-parse', 'HEAD^').decode().strip() == HEAD
    assert not git('status', '--porcelain=v1').strip()
    result = {'commit': commit, 'parent': HEAD, 'fixtures': FIXTURE,
        'passed_patch_sha256': PATCH, 'windows_gate_receipt': str(receipt_path),
        'windows_gate_receipt_sha256': sha(receipt_bytes), 'files_sha256': FILES}
    output = TASK / 'font-resolution-commit.json'
    assert not output.exists()
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result), flush=True)

if __name__ == '__main__':
    main()
