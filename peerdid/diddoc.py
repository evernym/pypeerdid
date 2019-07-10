import base64
import hashlib
import json

from .file import File


class DIDDoc:
    def __init__(self, path_or_file):
        if isinstance(path_or_file, File):
            self.file = path_or_file
        else:
            self.file = File(path_or_file)
        self._did = None
        self._genesis_doc = None

    @property
    def genesis_doc(self):
        if self._genesis_doc is None:
            if self.file and self.file.deltas:
                first = self.file.deltas[0]
                self._genesis_doc = base64.b64decode(first.change)
        return self._genesis_doc

    def apply_delta(self, json_dict, delta):
        change_fragment = json.loads(base64.b64decode(delta.change))

        def add_to_list(list_name, container):
            d = container.get(list_name)
            if d:
                items = json_dict.get(list_name)
                if not items:
                    items = json_dict[list_name] = []
                items.append(d[0])
                return d[0]

        def find_item_by_id(list, id):
            if list:
                for item in list:
                    if item.id == id:
                        return list, item

        deleted_id = add_to_list('deleted', change_fragment)
        if deleted_id:
            list, found = find_item_by_id(json_dict.get('publicKey'), deleted_id)
            if found:
                list.remove(found)
            json_dict.get('authentication', []).remove(deleted_id)
            list, found = find_item_by_id(json_dict.get('authorization', {}).get('profiles'), deleted_id)
            if found:
                list.remove(found)
        if add_to_list('publicKey', change_fragment):
            add_to_list('authentication', change_fragment)
            add_to_list('profiles', change_fragment.get('authorization', []))
        add_to_list('rules', change_fragment)

    def resolve(self, as_of:str = None) -> dict:
        gd = self.genesis_doc
        if gd:
            json_dict = json.loads(gd)
            first = True
            for item in self.file.deltas:
                if first:
                    first = False
                    continue
                if as_of and (item.when > as_of):
                    break
                self.apply_delta(json_dict, item)
            json_dict['id'] = self.did
            return json_dict

    @property
    def current_version(self):
        return len(self.file.deltas) if self.file.deltas else 0

    @property
    def did(self) -> str:
        if not self._did:
            gd = self.genesis_doc
            hash = hashlib.sha256(gd).hexdigest()
            self._did = 'did:peer:11-' + hash
        return self._did


_predefined_diddoc_template = """
{
    "@context": "https://w3id.org/did/v0.11",
    "id": "did:peer:11-%s",
    "service": [{
        "type": "did-communication",
        "serviceEndpoint": "https://localhost:12345"
    }],
    "publicKey": [
        {
            "id": "key-1",
            "type": "Ed25519VerificationKey2018",
            "publicKeyBase58": "GBMBzuhw7XgSdbNffh8HpoKWEdEN6hU2Q5WqL1KQTG5Z"
        },
        {
            "id": "key-3",
            "type": "Secp256k1VerificationKey2018",
            "controller": "#id",
            "publicKeyHex": "3056301006072a8648ce3d020106052b8104000a03420004a34521c8191d625ff811c82a24a60ff9f174c8b17a7550c11bba35dbf97f3f04392e6a9c6353fd07987e016122157bf56c487865036722e4a978bb6cd8843fa8"
        },
        {
            "id": "key-5",
            "type": "RsaVerificationKey2018",
            "controller": "#id",
            "publicKeyPem": "-----BEGIN PUBLIC KEY-----\r\nMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAoZp7md4nkmmFvkoHhQMw\r\nN0lcpYeKfeinKir7zYWFLmpClZHawZKLkB52+nnY4w9ZlKhc4Yosrw/N0h1sZlVZ\r\nfOQBnzFUQCea6uK/4BKHPhiHpN73uOwu5TAY4BHS7fsXRLPgQFB6o6iy127o2Jfb\r\nUVpbNU/rJGxVI2K1BIzkfrXAJ0pkjkdP7OFE6yRLU4ZcATWSIPwGvlF6a0/QPC3B\r\nbTvp2+DYPDC4pKWxNF/qOwOnMWqxGq6ookn12N/GufA/Ugv3BTVoy7I7Q9SXty4u\r\nUat19OBJVIqBOMgXsyDz0x/C6lhBR2uQ1K06XRa8N4hbfcgkSs+yNBkLfBl7N80Q\r\n0Wkq2PHetzQU12dPnz64vvr6s0rpYIo20VtLzhYA8ZxseGc3s7zmY5QWYx3ek7Vu\r\nwPv9QQzcmtIQQsUbekPoLnKLt6wJhPIGEr4tPXy8bmbaThRMx4tjyEQYy6d+uD0h\r\nXTLSjZ1SccMRqLxoPtTWVNXKY1E84EcS/QkqlY4AthLFBL6r+lnm+DlNaG8LMwCm\r\ncz5NMag9ooM9IqgdDYhUpWYDSdOvDubtz1YZ4hjQhaofdC2AkPXRiQvMy/Nx9WjQ\r\nn4z387kz5PK5YbadoZYkwtFttmxJ/EQkkhGEDTXoSRTufv+qjXDsmhEsdaNkvcDP\r\n1uiCSY19UWe5LQhIMbR0u/0CAwEAAQ==\r\n-----END PUBLIC KEY-----"
        }
    ],
    "authentication": ["#key-1", "#key-3", "#key-5"]
}
"""


def get_predefined(which) -> str:
    which = which[0].lower()
    if which in '01234d':
        return _predefined_diddoc_template % which*64
    elif which == 'c':
        return 'invalid DID doc'
    elif which == 'e':
        return """{
    "@context": "https://w3id.org/did/v0.11",
    "service": [],
    "publicKey": [],
    "authentication": []
}
"""

class ValidationError(BaseException):
    def __init__(self, msg):
        BaseException.__init__(self, msg)


def validate(json_text):
    if isinstance(json_text, bytes):
        json_text = json_text.decode("utf-8")
    elif not isinstance(json_text, str):
        raise ValidationError('Bad datatype. Expected string, not %s.' % json_text.__class__.__name__)
    try:
        j = json.loads(json_text)
    except:
        raise ValidationError('Invalid JSON.')
