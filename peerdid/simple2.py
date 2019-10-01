"""
Gives layer2 support for peer DIDs -- static DID docs. 30 min of coding to port.
"""

import base58 # Must use bitcoin's alphabet, not Flickr's.
import hashlib
import os
import re

# Use to detect whether a string is a valid peer DID. Parses into capture groups
# (1=numalgo, 2=base, 3=encnumbasis).
PEER_DID_PAT = re.compile(r'^did:peer:(1)(z)([1-9a-km-zA-HJ-NP-Z]{45})$')

# Where to store peer DIDs?
PEER_DID_STORAGE_FOLDER = os.path.expanduser('~/.peerdids')

DID_DOC_FILE_EXTENSION = '.diddoc'


def get_did_from_doc(stored_variant_did_doc_bytes):
    """
    Given the bytes of a stored variant of a genesis DID doc, get the corresponding DID.
    """

    # Optional fanciness not shown here:
    #
    # 1. Tolerate the resolved variant of a DID doc, and/or the DID doc passed in as a
    #    string instead of byte array, or as a python dict built by python's json module.
    # 2. Input validation (make sure DID doc is valid, incl requiring a key with the 'register'
    #    privilege).

    return 'did:peer:1z' + base58.b58encode(b'\x12' + hashlib.sha256(stored_variant_did_doc_bytes).digest()).encode('ascii')


def save_did(stored_variant_did_doc_bytes):
    """
    Persists a peer DID doc to disk so it can be used to resolve the DID later. Throws on error.
    """
    fname = os.path.join(PEER_DID_STORAGE_FOLDER, get_did_from_doc(stored_variant_did_doc_bytes) + '.diddoc')

    # Optional fanciness not shown here:
    #
    # 1. Tolerate the resolved variant of a DID doc. (Detect it by checking for the presence of
    #    a top-level "id" property, and subtract it to get the stored variant.)
    # 2. Specify a different folder where DID docs are stored.
    # 3. Input validation (make sure DID doc is valid).

    with open(fname, 'wb') as f:
        f.write(stored_variant_did_doc_bytes)


def resolve_did(did):
    """
    Given a peer DID, looks on disk to see if we have its DID doc. If yes, turns the on-disk, stored
    variant of the data into a resolved variant of a DID doc, and returns that variant as byte array.
    Returns None if DID is unknown. Throws on error.
    """

    # Optional fanciness not shown here:
    #
    # 1. Specify a different folder where DID docs are stored.
    # 2. Input validation (make sure DID value is valid).

    fname = os.path.join(PEER_DID_STORAGE_FOLDER, did + '.diddoc')
    if os.path.isfile(fname):
        with open(fname, 'rb') as f:
            stored_variant_did_doc_bytes = f.read()
        i = stored_variant_did_doc_bytes.rfind('}')
        return stored_variant_did_doc_bytes[:i] + '"id": "%s"' % did + stored_variant_did_doc_bytes[i:]


# Dependencies for the following function.
import json
import sgl # SGL defined on pypi and on npm; 200 lines of code to port for other langs

def is_authorized(privilege, did_doc, *keys):
    """
    Given a named privilege, a DID doc, and one or more keys, return True if the keys
    are collectively authorized to exercise the privilege. Throws on error.
    """
    parsed = json.loads(did_doc)

    # Find the profiles (assigned roles, like "edge" or "cloud") for each key.
    profiles = parsed['authorization']['profiles']
    defined_keys = []
    for k in keys:
        found = [p for p in profiles if p['id'] == k]
        if found:
            defined_keys.append(found[0])

    # Now look for rules that might grant the desired privilege.
    rules = parsed['authorization']['rules']
    for rule in rules:
        if privilege in rule['grant']:
            if sgl.satisfies(defined_keys, rule):
                return True
    return False

