import json
import os

from .delta import Delta


class Store:
    def __init__(self, fname):
        self.fname = os.path.abspath(fname)
        self.deltas = []
        self.dirty = False
        if os.path.exists(self.fname):
            self.load()

    def load(self):
        self.deltas = []
        with open(self.fname, 'rt') as f:
            for line in f:
                line = line.strip()
                if line.startswith('{') and line.endswith('}'):
                    self.deltas.append(Delta.from_json(line))
        self.dirty = False

    def save(self):
        if self.dirty:
            with open(self.fname, 'wt') as f:
                for d in self.deltas:
                    f.write(d.to_json() + '\n')
            self.dirty = False

    def append(self, delta):
        self.deltas.append(delta)
        self.dirty = True
        self.save()

    def __iter__(self):
        return self.deltas.__iter__()