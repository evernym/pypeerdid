# Software that supports Level 1 of the peer DID spec is able to recognize peer DIDs,
# and to compare, validate, and handle them correctly. These features are directly
# observable in our peerdid package.

import os
import pytest

from .. import is_valid_peer_did, compare_peer_dids, is_reserved_peer_did

data_folder = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                            'compliance/level-1'))


def get_file_text(path):
    with open(path, 'rt') as f:
        return f.read().strip()


def all_files_by_prefix(prefix):
    for path in os.listdir(data_folder):
        if path.startswith(prefix):
            yield path, get_file_text(os.path.join(data_folder, path))


def check_data_files(prefix, error_template, test_func):
    errors = []
    n = 0
    for path, value in all_files_by_prefix(prefix):
        n += 1
        if not test_func(value):
            errors.append(error_template % (value, path))
    assert n > 0
    if errors:
        pytest.fail('\n' + '\n'.join(errors))


def test_good_dids():
    check_data_files('good-did', 'Expected "%s" from %s to be a valid peer DID.', is_valid_peer_did)


def test_bad_dids():
    check_data_files('bad-did', 'Expected "%s" from %s to not be a valid peer DID.', lambda x: not is_valid_peer_did(x))


def comparable_pairs(path):
    with open(os.path.join(data_folder, path), 'rt') as f:
        lines = f.readlines()
    i = 0
    while i < len(lines) - 1:
        a = lines[i].strip()
        b = lines[i+1].strip()
        yield a, b
        i += 2

def reversed_pairs(path):
    for a, b in comparable_pairs(path):
        yield b, a

def check_comparables(generator, path, expected):
    errors = []
    n = 0
    for a, b in generator(path):
        n += 1
        actual = compare_peer_dids(a, b)
        actual = -1 if actual < 0 else (1 if actual > 0 else 0)
        if actual != expected:
            errors.append("Expected cmp(%s, %s) to be %d, not %d." % (a, b, expected, actual))
    assert n > 0
    if errors:
        pytest.fail('\n' + '\n'.join(errors))


def test_compare_equal():
    check_comparables(comparable_pairs, "compare-equal.txt", 0)


def test_compare_lt():
    check_comparables(comparable_pairs, "compare-lt.txt", -1)


def test_compare_gt():
    check_comparables(reversed_pairs, "compare-lt.txt", 1)


def test_is_reserved():
    chars = "0123456789abcdefx"
    for i in range(len(chars) - 1):
        c = chars[i]
        did = "did:peer:11-" + 64*c
        assert is_reserved_peer_did(did)
        assert is_reserved_peer_did(did[:13] + did[13:].upper())
        assert is_reserved_peer_did(did[:-5] + did[-5:].upper())
        assert not is_reserved_peer_did(did[:-1] + chars[i + 1])