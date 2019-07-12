import json
import os

from ..diddoc import get_predefined, get_path_where_diddocs_differ


def test_repo_empty_on_creation(scratch_repo):
    assert not os.listdir(scratch_repo.path)


def test_repo_creates_3_files(scratch_repo):
    scratch_repo.new_doc(get_predefined('0'))
    scratch_repo.new_doc(get_predefined('1'))
    scratch_repo.new_doc(get_predefined('2'))
    assert len(os.listdir(scratch_repo.path)) == 3


def test_repo_resolves_created_doc(scratch_repo):
    doc_0 = get_predefined('0')
    scratch_repo.new_doc(doc_0)
    # This is a bogus resolution in some ways; the doc had an "id" property but shouldn't have.
    assert scratch_repo.resolve('did:peer:11-0000000000000000000000000000000000000000000000000000000000000000') == \
        doc_0


def test_repo_resolves_correctly(scratch_repo):
    doc_0 = json.loads(get_predefined('0'))
    del doc_0['id']
    did = scratch_repo.new_doc(doc_0)
    resolved = scratch_repo.resolve(did)
    assert get_path_where_diddocs_differ(resolved, doc_0) == '.{id}'
    del resolved['id']
    assert get_path_where_diddocs_differ(resolved, doc_0) is None
