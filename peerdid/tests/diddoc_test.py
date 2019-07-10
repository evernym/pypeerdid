import base64
import pytest

from ..diddoc import *
from ..delta import Delta
from .. import is_valid_peer_did


def test_ctor(scratch_file):
    DIDDoc(scratch_file)


def test_did_property(scratch_file):
    dd = DIDDoc(scratch_file)
    fake_change = base64.b64encode(b'hello, world')
    delta = Delta(fake_change,[])
    dd.file.append(delta)
    did = dd.did
    assert is_valid_peer_did(dd.did)
    another_change = base64.b64encode(b'hello, yourself!')
    delta = Delta(another_change,[])
    dd.file.append(delta)
    assert dd.did == did


def test_serialize(scratch_file):
    dd1 = DIDDoc(scratch_file)
    change1 = base64.b64encode(get_predefined('0').encode("utf-8"))
    delta = Delta(change1, [])
    dd1.file.append(delta)
    dd2 = DIDDoc(scratch_file.path)
    assert dd1.did == dd2.did


def test_validate():
    with pytest.raises(ValidationError):
        validate(get_predefined('c'))