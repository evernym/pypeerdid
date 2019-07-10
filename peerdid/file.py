import os

from .delta import Delta


class File:
    """
    Backing storage for a single peer DID.
    """
    def __init__(self, path):
        self.path = os.path.normpath(path)
        self.deltas = []
        self.dirty = False
        if os.path.exists(self.path):
            self.load()

    def load(self):
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

    def append(self, delta):
        self.deltas.append(delta)
        self.dirty = True
        self.save()

    def __iter__(self):
        return self.deltas.__iter__()

