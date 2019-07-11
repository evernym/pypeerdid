import os


def test_repo_empty_on_creation(scratch_repo):
    assert not os.listdir(scratch_repo.path)


