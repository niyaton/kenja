from __future__ import absolute_import
from bisect import bisect_left
from itertools import (izip, repeat)
from kenja.git.util import tree_mode

class SortedTreeContents(object):
    def __init__(self, iterable=()):
        self._binshas = [i[0] for i in iterable]
        self._names = [i[1] for i in iterable]

    def __iter__(self):
        return izip(repeat(tree_mode), self._binshas, self._names)

    def index(self, name):
        pos = bisect_left(self._names, name)
        return pos if pos != len(self._names) and self._names[pos] == name else None

    def remove(self, name):
        pos = bisect_left(self._names, name)
        del self._names[pos]
        del self._binshas[pos]

    def insert(self, name, binsha):
        pos = bisect_left(self._names, name)
        self._names.insert(pos, name)
        self._binshas.insert(pos, binsha)

    def replace(self, name, binsha):
        pos = self.index(name)
        self._binshas[pos] = binsha

