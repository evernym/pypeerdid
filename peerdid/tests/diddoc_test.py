import pytest

from ..diddoc import *
from ..delta import Delta
from .. import is_valid_peer_did


BOGUS_CHANGE = b'{"say": "hello, world"}'


def test_ctor_with_File(scratch_file):
    DIDDoc(scratch_file)


def test_ctor_with_folder(scratch_space):
    DIDDoc(scratch_space.name)


def test_empty_doc_doesnt_have_did(scratch_space):
    dd = DIDDoc(scratch_space.name)
    assert not bool(dd.did)


def make_genesis_doc(folder, change):
    dd = DIDDoc(folder)
    delta = Delta(change,[])
    dd.append(delta)
    return dd


@pytest.fixture
def hw(scratch_space):
    yield make_genesis_doc(scratch_space.name, BOGUS_CHANGE)


def test_did_created_after_first_delta(hw):
    assert is_valid_peer_did(hw.did)


def test_did_value_tied_to_delta(scratch_space):
    dd1 = make_genesis_doc(scratch_space.name, BOGUS_CHANGE)
    dd2 = make_genesis_doc(scratch_space.name, b'{"say": "goodbye"}')
    dd3 = make_genesis_doc(scratch_space.name, BOGUS_CHANGE)
    assert dd1.did != dd2.did
    assert dd1.did == dd3.did


def test_second_delta_doesnt_change_did_value(hw):
    initial_did_value = hw.did
    delta = Delta('{"say": "hello, yourself!"}',[])
    hw.file.append(delta)
    assert hw.did == initial_did_value


def test_serialize(scratch_file):
    dd1 = DIDDoc(scratch_file)
    change1 = get_predefined('1').encode("utf-8")
    delta = Delta(change1, [])
    dd1.file.append(delta)
    dd2 = DIDDoc(scratch_file.path)
    assert dd1.did == dd2.did


def test_predefined_is_valid():
    for which in '12345d':
        validate(get_predefined(which))


def test_validate_catches_errors():
    invalid_docs = [
        {}, {"a":1}, [], 'hello', get_predefined('c')
    ]
    for invalid_doc in invalid_docs:
        with pytest.raises(BaseException):
            validate(invalid_doc)


def test_get_path_where_diddocs_differ():
    doc_0 = get_predefined('2')
    doc_1 = get_predefined('1')
    doc_2 = json.loads(doc_0)
    doc_2['publicKey'].append({'abc':1})
    doc_3 = json.loads(doc_0)
    doc_3['publicKey'][0]['abc'] = 1
    assert get_path_where_diddocs_differ(doc_0, doc_0) is None
    assert get_path_where_diddocs_differ(doc_0, doc_1) == '.id'
    assert get_path_where_diddocs_differ(doc_0, doc_2) == '.publicKey'
    assert get_path_where_diddocs_differ(doc_0, doc_3) == '.publicKey[0]'


def test_resolve(scratch_space):
    dd = make_genesis_doc(scratch_space.name, BOGUS_CHANGE)
    assert get_path_where_diddocs_differ(dd.resolve(),
        '{"id": "did:peer:1z6NRwAcQAJP8iFvVT3XqYcp97vtcuChXu9EzbZ9zJcMqdq", "say": "hello, world"}') is None