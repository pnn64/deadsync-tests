"""Derive reviewed statistics expectations solely from old rows and native contracts."""
from pathlib import Path
import hashlib
import json
import re
import struct
import subprocess

TASK = Path(__file__).resolve().parent
PRODUCT = TASK.parents[1]
FIXTURES = PRODUCT.parent / "deadsync-fixtures-lua-fleet-20261119"
NATIVE = PRODUCT.parent / "itgmania-harness/vendor/itgmania"
BASE = "234352ae735a4ec78230f2139e56fa3be734bedc"
REL = "regression-expectations/deadsync-song-lua/a74e87153021edf1.snap"
SOURCE = "crates/deadsync-song-lua/tests/statistics.rs"
TEST = "complete_manager_stage_and_player_surfaces_defaults_and_identities"
OUT = TASK / "played-stage-history-evidence/statistics-snapshot-proposal"
OUT.mkdir(parents=True, exist_ok=True)
assert not (OUT / "receipt.json").exists(), "A retained proposal already exists"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def identity(source):
    data = source.encode("utf-8")
    value = 0xcbf29ce484222325
    for byte in data:
        value = ((value ^ byte) * 0x100000001b3) & ((1 << 64) - 1)
    return len(data), value


def program_blocks(source):
    section = source.split("fn " + TEST + "() {", 1)[1].split("\n#[test]", 1)[0]
    blocks = re.findall(r'r#"(.*?)"#', section, re.S)
    assert len(blocks) == 3
    values = re.search(r'const VALUES:.*?= &\[(.*?)\];', source, re.S).group(1)
    values = [json.loads(value) for value in re.findall(r'"(?:[^"\\]|\\.)*"', values)]
    extra = re.search(r'\.chain\(\[(.*?)\]\)', section, re.S).group(1)
    values += [json.loads(value) for value in re.findall(r'"(?:[^"\\]|\\.)*"', extra)]
    return blocks, values


def parse_row(row):
    match = re.fullmatch(r'\((\d+), (\d+), \[(.*)\]\)', row)
    assert match, row[:80]
    values = re.findall(r'String\(\[[^]]*\]\)|Number\(\d+\)|Boolean\((?:true|false)\)|Nil', match[3])
    assert ', '.join(values) == match[3], 'Unexpected scalar representation'
    return (int(match[1]), int(match[2])), values


def encode_string(value):
    return 'String([' + ', '.join(str(byte) for byte in value.encode()) + '])'


def decode_string(value):
    return bytes(json.loads(value[7:-1])).decode()


def encode_number(value):
    return 'Number(' + str(struct.unpack('<Q', struct.pack('<d', value))[0]) + ')'


def decoded(values):
    result = []
    for value in values:
        if value.startswith('String('): result.append(decode_string(value))
        elif value.startswith('Number('): result.append(struct.unpack('<d', struct.pack('<Q', int(value[7:-1])))[0])
        elif value.startswith('Boolean('): result.append(value == 'Boolean(true)')
        else: result.append(None)
    return result


before = subprocess.check_output(['git', 'show', BASE + ':' + REL], cwd=FIXTURES)
old_source_bytes = subprocess.check_output(['git', 'show', 'HEAD:' + SOURCE], cwd=PRODUCT)
new_source_bytes = (PRODUCT / SOURCE).read_bytes()
old_source = old_source_bytes.decode().replace('\r\n', '\n')
new_source = new_source_bytes.decode().replace('\r\n', '\n')
old_blocks, old_values = program_blocks(old_source)
new_blocks, new_values = program_blocks(new_source)
assert old_values == new_values and len(old_values) == 26
lines = before.decode().splitlines(keepends=True)
positions = []
in_test = False
for index, line in enumerate(lines):
    if line.startswith('test: '): in_test = line.rstrip('\r\n') == 'test: ' + TEST
    elif in_test: positions.append(index)
assert len(positions) == 29
changes = []
invalid = {'nil', 'false', 'true', "' nope '", '{}', 'function()end', "'P1'", "'p2'", "'PlayerNumber_P2'"}
for case in range(1, 29):
    index = positions[case]
    row = lines[index].rstrip('\r\n')
    ending = lines[index][len(row):]
    old_input, values = parse_row(row)
    original = list(values)
    if case == 1:
        old_program, new_program = old_blocks[0], new_blocks[0]
        assert len(values) == 26
        keys = decode_string(values[1]).split(',')
        assert '__songlua_steps_seconds' not in keys
        values[1] = encode_string(','.join(sorted(keys + ['__songlua_steps_seconds'])))
        for player in (2, 3, 4):
            keys = decode_string(values[player]).split(',')
            assert '__songlua_alive_seconds' not in keys
            values[player] = encode_string(','.join(sorted(keys + ['__songlua_alive_seconds'])))
        assert values[5] == encode_number(1) and values[18] == encode_number(125.25)
        values[5] = encode_number(0)
        values[18] = encode_number(0)
        allowed = {1, 2, 3, 4, 5, 18}
        assert all(values[i] == original[i] for i in range(len(values)) if i not in allowed)
        reason = 'Actual stage count starts at zero; steps clock starts at zero; scalar publication adds only its owned private keys.'
    elif case == 28:
        old_program, new_program = old_blocks[2], new_blocks[2]
        assert len(values) == 9
        assert values[5] == encode_number(1) and values[6] == encode_number(1)
        values[5] = encode_number(100)
        values[6] = encode_number(100)
        assert all(values[i] == original[i] for i in range(len(values)) if i not in {5, 6})
        reason = 'Native GetLifeRecord requires last_second and substitutes 100 samples for nonpositive counts; all other defaults remain unchanged.'
    else:
        selector = old_values[case - 2]
        old_program = old_blocks[1].replace('{selector}', selector)
        new_program = new_blocks[1].replace('{selector}', selector)
        assert len(values) == 3
        accepted = 'Boolean(false)' if selector in invalid else 'Boolean(true)'
        values = values[:2] + [accepted, accepted]
        assert values[:2] == original[:2]
        reason = 'Native checkint accepts numbers/numeric strings; an empty played-stage vector has no result. Preserve both unrelated player-selector observations.'
    assert old_input == identity(old_program), (case, old_input, identity(old_program))
    length, digest = identity(new_program)
    replacement = f'({length}, {digest}, [' + ', '.join(values) + '])'
    assert replacement != row
    lines[index] = replacement + ending
    changes.append({'case': case, 'line': index + 1, 'old_input_identity': old_input,
                    'new_input_identity': [length, digest], 'before_values': decoded(original),
                    'after_values': decoded(values), 'reason': reason})

after = ''.join(lines).encode()
old_lines = before.splitlines(keepends=True)
new_lines = after.splitlines(keepends=True)
assert len(old_lines) == len(new_lines)
allowed_lines = {positions[case] for case in range(1, 29)}
assert all(a == b for index, (a, b) in enumerate(zip(old_lines, new_lines)) if index not in allowed_lines)
assert sum(a != b for a, b in zip(old_lines, new_lines)) == 28
(OUT / 'before.snap').write_bytes(before)
(OUT / 'after.snap').write_bytes(after)
(OUT / 'before-source.rs').write_bytes(old_source_bytes)
(OUT / 'after-source.rs').write_bytes(new_source_bytes)
authority = []
for name, regions in {
    'src/StatsManager.cpp': [(529, 567)],
    'src/StageStats.cpp': [(29, 55), (516, 518)],
    'src/PlayerStageStats.cpp': [(872, 892)],
    'src/LuaManager.h': [(269, 271)],
    'extern/lua-5.1/src/lauxlib.c': [(197, 201)],
    'extern/lua-5.1/src/lobject.c': [(90, 99)],
    'extern/lua-5.1/src/luaconf.h': [(519, 525)],
}.items():
    data = (NATIVE / name).read_bytes()
    source_lines = data.decode().splitlines()
    authority.append({'path': name, 'sha256': sha(data), 'regions': [
        {'first_line': a, 'last_line': b, 'text': '\n'.join(source_lines[a-1:b])} for a, b in regions]})
receipt = {'base_fixture_commit': BASE, 'relative_path': REL, 'test': TEST,
           'before_sha256': sha(before), 'after_sha256': sha(after),
           'old_source_sha256': sha(old_source_bytes), 'new_source_sha256': sha(new_source_bytes),
           'changed_rows': changes, 'all_unrelated_rows_byte_equal': True,
           'actual_output_used_as_expectation': False,
           'native_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=NATIVE, text=True).strip(),
           'authority': authority}
(OUT / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'proposal': str(OUT), 'before_sha256': sha(before), 'after_sha256': sha(after),
                  'rows_changed': len(changes), 'receipt_sha256': sha((OUT / 'receipt.json').read_bytes())}))
