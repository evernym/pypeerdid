import os

from ..delta import Delta


def test_is_iterable(scratch_file):
    for item in scratch_file:
        return


def test_file_io(scratch_file):
    assert not os.path.exists(scratch_file.path)
    scratch_file.append(Delta("abc", []))
    assert os.path.exists(scratch_file.path)