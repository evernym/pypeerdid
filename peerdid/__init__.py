import re

PEER_DID_PAT = re.compile(r'^did:peer:11-[a-fA-F0-9]{64}$')


def is_valid_peer_did(did: str):
    if did:
        return bool(PEER_DID_PAT.match(did))


def is_reserved_peer_did(did: str):
    if did:
        m = PEER_DID_PAT.match(did)
        if m:
            c = did[13].lower()
            for i in range(14, 76):
                if did[i].lower() != c:
                    return False
            return True
    return False


def compare_peer_dids(did_a, did_b):
    prefix_a = did_a[:12]
    prefix_b = did_b[:12]
    # Compare the prefix case-sensitively.
    n = -1 if prefix_a < prefix_b else (1 if prefix_a > prefix_b else 0)
    if n == 0:
        # Don't use .localeCompare() or .toLocaleLowerCase();
        # we want raw ASCII comparison. Just normalize to
        # lower case before comparing.
        numeric_a = did_a[12:].lower()
        numeric_b = did_b[12:].lower()
        n = -1 if numeric_a < numeric_b else (1 if numeric_a > numeric_b else 0)
    return n