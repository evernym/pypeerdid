import os
import pytest
import tempfile


from ..file import File


@pytest.fixture
def scratch_space():
    x = tempfile.TemporaryDirectory()
    yield x
    x.cleanup()

@pytest.fixture
def scratch_file(scratch_space):
    x = File(os.path.join(scratch_space.name, 'peerdid-file'))
    yield x


