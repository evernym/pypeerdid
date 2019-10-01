import os

from .delta import Delta


class FileMisuseError(IOError):
    def __init__(self, msg):
        IOError.__init__(self, msg)


class File:
    """
    Provides backing storage for a single peer DID.
    """

    def __init__(self, path, autosave=True):
        self.path = os.path.normpath(path)
        self.deltas = []
        self.dirty = False
        self.autosave = autosave
        self._did = None
        if os.path.exists(self.path):
            self.load()

    def load(self, ignore_dirty=False):
        if (not ignore_dirty) and self.dirty:
            raise FileMisuseError("Can't load while in the dirty state.")
        self.deltas = []
        with open(self.path, 'rt') as f:
            for line in f:
                line = line.strip()
                if line.startswith('{') and line.endswith('}'):
                    self.deltas.append(Delta.from_json(line))
        self.dirty = False

    def save(self):
        if self.dirty:
            with open(self.path, 'wt') as f:
                for d in self.deltas:
                    f.write(d.to_json() + '\n')
            self.dirty = False

    def append(self, delta: Delta, autosave: bool = None):
        self.deltas.append(delta)
        self.dirty = True
        if autosave is None:
            autosave = self.autosave
        if autosave:
            self.save()

    @property
    def genesis(self) -> Delta:
        if self.deltas:
                return self.deltas[0]

    @property
    def did(self) -> str:
        if self._did is None:
            g = self.genesis
            if g:
                self._did = 'did:peer:1z' + g.encnumbasis
        return self._did


def canonical_fname(did_or_hash):
    if did_or_hash.startswith('did:peer:1z'):
        did_or_hash = did_or_hash[11:]
    return did_or_hash + ".ddd"