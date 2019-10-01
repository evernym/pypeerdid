import json
import os

from ..diddoc import get_predefined, get_path_where_diddocs_differ


def test_repo_empty_on_creation(scratch_repo):
    assert not os.listdir(scratch_repo.path)


def test_repo_creates_3_files(scratch_repo):
    scratch_repo.new_doc(get_predefined('1'))
    scratch_repo.new_doc(get_predefined('2'))
    scratch_repo.new_doc(get_predefined('3'))
    assert len(os.listdir(scratch_repo.path)) == 3


def test_repo_resolves_created_doc(scratch_repo):
    doc_1 = get_predefined('1')
    scratch_repo.new_doc(doc_1)
    # This is a bogus resolution in some ways; the doc had an "id" property but shouldn't have.
    assert scratch_repo.resolve('did:peer:1z111111111111111111111111111111111111111111111') == \
        doc_1


def test_repo_resolves_correctly(scratch_repo):
    doc_1 = json.loads(get_predefined('1'))
    del doc_1['id']
    did = scratch_repo.new_doc(doc_1)
    resolved = scratch_repo.resolve(did)
    assert get_path_where_diddocs_differ(resolved, doc_1) == '.{id}'
    del resolved['id']
    assert get_path_where_diddocs_differ(resolved, doc_1) is None
