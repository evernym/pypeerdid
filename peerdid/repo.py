import os

from .diddoc import DIDDoc, get_predefined
from .delta import Delta
from . import is_valid_peer_did, is_reserved_peer_did


def _fname_for_did(folder, did):
    return os.path.join(folder, did[13:] + '-deltas.txt')


class Repo:
    """
    Backing storage for all known peer DIDs.
    """
    def __init__(self, path):
        assert os.path.isdir(path)
        self.path = os.path.normpath(path)


    def new_doc(self, genesis_doc, signatures=[]):
        delta = Delta(genesis_doc, signatures)
        doc = DIDDoc(delta)


    def resolve(self, did, as_of_time=None):
        if is_valid_peer_did(did):
            if is_reserved_peer_did(did):
                return get_predefined(did[13])
            else:
                path = _fname_for_did(did)
                if os.path.isfile(path):
                    doc = DIDDoc(path)
                    return doc.resolve(as_of_time)
