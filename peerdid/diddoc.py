from .storage import Store

class DIDDoc:
    def __init__(self, fname):
        self.store = Store(fname)
        