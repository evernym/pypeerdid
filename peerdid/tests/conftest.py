import os
import pytest
import tempfile


from ..file import File
from ..repo import Repo
from ..delta import Delta


@pytest.fixture
def scratch_space():
    x = tempfile.TemporaryDirectory()
    yield x
    x.cleanup()


@pytest.fixture
def scratch_file(scratch_space):
    x = File(os.path.join(scratch_space.name, 'peerdid-file'))
    yield x


@pytest.fixture
def scratch_repo(scratch_space):
    x = Repo(scratch_space.name)
    yield x


@pytest.fixture
def sample_delta():
    return Delta('{"deleted": ["key-1"]}', [])