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
        return True


xs = [r"([\*0-9a-zA-Z]+[\.\-])*[\*0-9a-zA-Z]+", "\s*(-|=|>=?|<=?|\|{2})\s*", "~|~>", "\^", "\s+"]


def get_sym(scanner, x):
    return x

scanner = re.Scanner([(x, get_sym) for x in xs])


def parse(expr):
    xs = scanner.scan(expr)
    if xs[1] != "":
        raise Exception((xs[0], xs[1]))
    return [x.strip() for x in xs[0] if x.strip() != '']

range_cands = [
    ['1.0.0 - 2.0.0', '1.2.3', True],
    ['1.0.0', '1.0.0', True],
    ['>=*', '0.2.4', True],
    ['', '1.0.0', True],
    ['*', '1.2.3', True],
    ['*', 'v1.2.3-foo', True],
    ['>=1.0.0', '1.0.0', True],
    ['>=1.0.0', '1.0.1', True],
    ['>=1.0.0', '1.1.0', True],
    ['>1.0.0', '1.0.1', True],
    ['>1.0.0', '1.1.0', True],
    ['<=2.0.0', '2.0.0', True],
    ['<=2.0.0', '1.9999.9999', True],
    ['<=2.0.0', '0.2.9', True],
    ['<2.0.0', '1.9999.9999', True],
    ['<2.0.0', '0.2.9', True],
    ['>= 1.0.0', '1.0.0', True],
    ['>=  1.0.0', '1.0.1', True],
    ['>=   1.0.0', '1.1.0', True],
    ['> 1.0.0', '1.0.1', True],
    ['>  1.0.0', '1.1.0', True],
    ['<=   2.0.0', '2.0.0', True],
    ['<= 2.0.0', '1.9999.9999', True],
    ['<=  2.0.0', '0.2.9', True],
    ['<    2.0.0', '1.9999.9999', True],
    ['<\t2.0.0', '0.2.9', True],
    ['>=0.1.97', 'v0.1.97', True],
    ['>=0.1.97', '0.1.97', True],
    ['0.1.20 || 1.2.4', '1.2.4', True],
    ['>=0.2.3 || <0.0.1', '0.0.0', True],
    ['>=0.2.3 || <0.0.1', '0.2.3', True],
    ['>=0.2.3 || <0.0.1', '0.2.4', True],
    ['||', '1.3.4', True],
    ['2.x.x', '2.1.3', True],
    ['1.2.x', '1.2.3', True],
    ['1.2.x || 2.x', '2.1.3', True],
    ['1.2.x || 2.x', '1.2.3', True],
    ['x', '1.2.3', True],
    ['2.*.*', '2.1.3', True],
    ['1.2.*', '1.2.3', True],
    ['1.2.* || 2.*', '2.1.3', True],
    ['1.2.* || 2.*', '1.2.3', True],
    ['*', '1.2.3', True],
    ['2', '2.1.2', True],
    ['2.3', '2.3.1', True],
    ['~2.4', '2.4.0', True],  #  >=2.4.0 <2.5.0
    ['~2.4', '2.4.5', True],
    ['~>3.2.1', '3.2.2', True],  #  >=3.2.1 <3.3.0,
    ['~1', '1.2.3', True],  #  >=1.0.0 <2.0.0
    ['~>1', '1.2.3', True],
    ['~> 1', '1.2.3', True],
    ['~1.0', '1.0.2', True],  #  >=1.0.0 <1.1.0,
    ['~ 1.0', '1.0.2', True],
    ['~ 1.0.3', '1.0.12', True],
    ['>=1', '1.0.0', True],
    ['>= 1', '1.0.0', True],
    ['<1.2', '1.1.1', True],
    ['< 1.2', '1.1.1', True],
    ['1', '1.0.0beta', True],
    ['~v0.5.4-pre', '0.5.5', True],
    ['~v0.5.4-pre', '0.5.4', True],
    ['=0.7.x', '0.7.2', True],
    ['>=0.7.x', '0.7.2', True],
    ['=0.7.x', '0.7.0-asdf', True],
    ['>=0.7.x', '0.7.0-asdf', True],
    ['<=0.7.x', '0.6.2', True],
    ['~1.2.1 >=1.2.3', '1.2.3', True],
    ['~1.2.1 =1.2.3', '1.2.3', True],
    ['~1.2.1 1.2.3', '1.2.3', True],
    ['~1.2.1 >=1.2.3 1.2.3', '1.2.3', True],
    ['~1.2.1 1.2.3 >=1.2.3', '1.2.3', True],
    ['~1.2.1 1.2.3', '1.2.3', True],
    ['>=1.2.1 1.2.3', '1.2.3', True],
    ['1.2.3 >=1.2.1', '1.2.3', True],
    ['>=1.2.3 >=1.2.1', '1.2.3', True],
    ['>=1.2.1 >=1.2.3', '1.2.3', True],
    ['<=1.2.3', '1.2.3-beta', True],
    ['>1.2', '1.3.0-beta', True],
    ['>=1.2', '1.2.8', True],
    ['^1.2.3', '1.8.1', True],
    ['^1.2.3', '1.2.3-beta', True],
    ['^0.1.2', '0.1.2', True],
    ['^0.1', '0.1.2', True],
    ['^1.2', '1.4.2', True],
    ['^1.2 ^1', '1.4.2', True],
    ['^1.2', '1.2.0-pre', True],
    ['^1.2.3', '1.2.3-pre', True]
]


# range_cands = [
#     ['<=   2.0.0', '2.0.0', True],
#     ['<= 2.0.0', '1.9999.9999', True],
#     ['<=  2.0.0', '0.2.9', True],
#     ['<    2.0.0', '1.9999.9999', True],
# ]


for xs in range_cands:
    print("[%r, %r]," % (xs[0], parse(xs[0])))

# print(parse('1.0.0 - 2.0.0'))
