import os
import pytest
import tempfile

from ..delta import Delta
from ..storage import Store

@pytest.fixture
def scratch_space():
    x = tempfile.TemporaryDirectory()
    yield x
    x.cleanup()

@pytest.fixture
def store(scratch_space):
    x = Store(os.path.join(scratch_space.name, 'store'))
    yield x


def test_is_iterable(store):
    for x in store:
        pass


def test_file_io(store):
    assert not os.path.exists(store.fname)
    store.append(Delta("abc", []))
    assert os.path.exists(store.fname)