import os

class Store:
    def __init__(self, fname):
        self.fname = os.path.abspath(fname)
        self.deltas = []
    def append(self, delta):
        self.deltas.append(delta)
    def __iter__(self):
        return self.deltas.__iter__()