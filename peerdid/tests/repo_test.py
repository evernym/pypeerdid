import os


def test_repo_empty_on_creation(scratch_repo):
    assert not os.listdir(scratch_repo.path)


def test_repo_creates_3_files(scratch_repo):
    scratch_repo.new_doc()