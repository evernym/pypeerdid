import os

from .diddoc import DIDDoc
from . import is_valid_peer_did, is_reserved_peer_did


def _fname_for_did(folder, did):
    return os.path.join(folder, did[13:] + '-deltas.txt')


class Repo:
    """
    Backing storage for all known peer DIDs.
    """
    def __init__(self, folder):
        assert os.path.isdir(folder)
        self.folder = os.path.normpath(folder)

    def resolve(self, did, as_of_time=None):
        if is_valid_peer_did(did):
            if is_reserved_peer_did(did):
                return _get_predefined_diddoc(did[13])
            else:
                path = _fname_for_did(did)
                if os.path.isfile(path):
                    doc = DIDDoc(path)
                    return doc.resolve(as_of_time)
