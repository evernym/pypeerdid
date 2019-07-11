import os
import pytest

from ..delta import Delta


def test_genesis(scratch_file, sample_delta):
    assert (scratch_file.genesis is None)
    scratch_file.append(sample_delta)
    assert bool(scratch_file.genesis)


def test_did(scratch_file, sample_delta):
    assert (scratch_file.did is None)
    scratch_file.append(sample_delta)
    assert bool(scratch_file.did)


def test_autosave(scratch_file, sample_delta):
    assert not os.path.exists(scratch_file.path)
    scratch_file.append(sample_delta)
    assert os.path.exists(scratch_file.path)


def test_autosave_false(scratch_file, sample_delta):
    scratch_file.autosave = False
    assert not os.path.exists(scratch_file.path)
    scratch_file.append(sample_delta)
    assert not os.path.exists(scratch_file.path)
    scratch_file.save()
    assert os.path.exists(scratch_file.path)