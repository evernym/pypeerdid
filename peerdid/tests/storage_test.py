import os
import pytest
import tempfile

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