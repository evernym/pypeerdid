import re

PEER_DID_PAT = re.compile(r'^did:peer:(1)(z)([1-9a-km-zA-HJ-NP-Z]{45})$')


def is_valid_peer_did(did: str):
    if did:
        return bool(PEER_DID_PAT.match(did))


def is_reserved_peer_did(did: str):
    if did:
        m = PEER_DID_PAT.match(did)
        if m:
            c = did[11].lower()
            for i in range(12, 56):
                if did[i].lower() != c:
                    return False
            return True
    return False


def compare_peer_dids(did_a, did_b):
    # Right now, we only know how to compare DIDs that use base58 encoding.
    # that comparison is case-sensitive.
    assert did_a[10] == 'z'
    assert did_b[10] == 'z'
    return -1 if did_a < did_b else 1 if did_a > did_b else 0
