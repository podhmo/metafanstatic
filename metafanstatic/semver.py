# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

"""
sub set of isaacs/node-semver
https://github.com/isaacs/node-semver
"""
from itertools import zip_longest
from distutils.version import Version
import re


class SemverVersion(Version):
    component_re = re.compile(r'(\d+ | [a-zA-Z]+ | \.)', re.VERBOSE)

    def normalize(self, x):
        x = x.lstrip("vV= ")
        return x

    def parse(self, vstring):
        vstring = self.normalize(vstring)

        self.vstring = vstring
        components = [x for x in self.component_re.split(vstring) if x and x != '.']
        for i, obj in enumerate(components):
            try:
                components[i] = int(obj)
            except ValueError:
                pass

        self.version = components

    def safe_int(self, x):
        try:
            return int(x)
        except ValueError:
            return None

    def __repr__(self):
        return "%s (%s)" % (self.__class__.__name__, (self.vstring))

    def _cmp(self, other):
        if isinstance(other, str):
            other = self.__class__(other)
        c = 0
        try:
            for i, (x, y) in enumerate(zip_longest(self.version, other.version)):
                if y is None:
                    if isinstance(self.version[c - 1], int):
                        return -1
                    else:
                        return 1
                if x is None:
                    if isinstance(self.version[c - 1], int):
                        return 1
                    else:
                        return -1
                if x < y:
                    return -1
                if x > y:
                    return 1
                c += 1
                if "-" == x or y == "-":
                    raise TypeError("")
            return 0
        except TypeError:
            for x, y in zip_longest(self.version[c:], other.version[c:]):
                if x is None:
                    return -1
                if y is None:
                    return 1
                ix = self.safe_int(x)
                iy = self.safe_int(y)
                if ix and iy:
                    if ix < iy:
                        return -1
                    if ix > iy:
                        return 1
                sx = str(x)
                sy = str(y)
                if sx < sy:
                    return -1
                if sx > sy:
                    return 1
            return 0

    def __contains__(self, other):
        pass

