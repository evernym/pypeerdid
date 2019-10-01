import os

from .diddoc import DIDDoc, get_predefined
from .delta import Delta
from .file import File, canonical_fname
from . import is_valid_peer_did, is_reserved_peer_did


class Repo:
    """
    Backing storage for a collection of peer DIDs.
    """
    def __init__(self, path):
        assert os.path.isdir(path)
        self.path = os.path.normpath(path)

    def new_doc(self, genesis_doc, signatures=[]):
        delta = Delta(genesis_doc, signatures)
        path = os.path.join(self.path, canonical_fname(delta.encnumbasis))
        f = File(path)
        f.append(delta)
        return f.did


    def resolve(self, did, as_of_time=None):
        if is_valid_peer_did(did):
            if is_reserved_peer_did(did):
                return get_predefined(did[13])
            else:
                path = os.path.join(self.path, canonical_fname(did))
                if os.path.isfile(path):
                    doc = DIDDoc(path)
                    return doc.resolve(as_of_time)
