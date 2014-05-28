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
    component_re = re.compile(r'(\d+ | [a-zA-Z\*]+ | \.)', re.VERBOSE)

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
        return "%s (%s)" % (self.__class__.__name__, (self.version))

    def _cmp(self, other):
        if isinstance(other, str):
            other = self.__class__(other)
        try:
            for c, (x, y) in enumerate(zip_longest(self.version, other.version)):
                if x == "x" or x == "*":
                    continue
                if y == "y" or y == "*":
                    continue

                if y is None:
                    if len(self.version) == c + 1 and self.version[-1] == 0:
                        return 0
                    elif isinstance(self.version[c - 1], int) and isinstance(y, str):
                        return 1
                    elif self.version[c - 1] == "x" or self.version[c - 1] == "*":
                        return -1
                    else:
                        return 1
                if x is None:
                    if len(other.version) == c + 1 and other.version[-1] == 0:
                        return 0
                    elif isinstance(self.version[c - 1], int) and isinstance(y, str):
                        return 1
                    elif self.version[c - 1] == "x" or self.version[c - 1] == "*":
                        return 1
                    else:
                        return -1
                if x < y:
                    return -1
                if x > y:
                    return 1
                if "+" == x or y == "+":
                    return 0
                if "-" == x or y == "-":
                    raise TypeError("")
            return 0
        except TypeError:
            for x, y in zip_longest(self.version[c:], other.version[c:]):
                if "+" == x or y == "+":
                    return 0
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

    def copy(self):
        v = SemverVersion(None)
        v.version = self.version.copy()
        v.vstring = self.vstring
        return v

    def verup(self):
        copied = self.copy()
        for i, x in enumerate(copied.version):
            if not isinstance(x, int):
                v = list(copied.version)
                v[i - 2] += 1
                for i in range(len(v) - i + 1):
                    v.pop()
                copied.version = v
                break
        else:
            if len(copied.version) == 1:
                copied.version = [copied.version[-1] + 1]
            else:
                v = list(copied.version)
                v[-2] += 1
                v[-1] = 0
                copied.version = v
        return copied

    def neary_equal(self, other):
        for x, y in zip_longest(self.version, other.version):
            if x == y:
                continue
            if x == "x" or x == "*":
                continue
            if x is None:
                return True
            return False
        return True


def ver_range(region, version):
    parsed = parse(region)
    n = len(parsed)
    return ver_range_execute(parsed, n, version)


def ver_range_execute(parsed, n, version):
    print(parsed, n)
    if n == 0:
        return True
    if n == 1:
        if parsed[0] == "*" or parsed[0] == "||":
            return True
        return SemverVersion(parsed[0]).neary_equal(SemverVersion(version))
    if n == 2:
        if parsed[1] == "*":
            return True
        else:
            if "~" == parsed[0] or "~>" == parsed[0]:  # xxx
                v = SemverVersion(parsed[1])
                print("@", v, "<=", SemverVersion(version), "<", v.verup(), "@")
                print("@", v <= SemverVersion(version))
                print(SemverVersion(version) < v.verup(), "@")
                return v <= SemverVersion(version) < v.verup()
            elif "^" == parsed[0]:
                raise Exception((n, parsed))
            elif "=" == parsed[0]:
                return SemverVersion(parsed[1]) == SemverVersion(version)
            elif ">=" == parsed[0]:
                return SemverVersion(parsed[1]) <= SemverVersion(version)
            elif ">" == parsed[0]:
                return SemverVersion(parsed[1]) < SemverVersion(version)
            elif "<=" == parsed[0]:
                return SemverVersion(parsed[1]) >= SemverVersion(version)
            elif "<" == parsed[0]:
                return SemverVersion(parsed[1]) > SemverVersion(version)
            raise Exception((n, parsed))
    if n == 3:
        if parsed[1] == "-":
            return SemverVersion(parsed[0]) <= SemverVersion(version) <= SemverVersion(parsed[2])
        elif parsed[1] == "||":
            return ver_range_execute([parsed[0]], 1, version) or ver_range_execute([parsed[2]], 1, version)
        elif parsed[1] == "=":
            return ver_range_execute([parsed[0]], 1, version) == ver_range_execute([parsed[2]], 1, version)
        elif parsed[1] == ">=":
            return ver_range_execute([parsed[0]], 1, version) >= ver_range_execute([parsed[2]], 1, version)
        elif parsed[1] == ">":
            return ver_range_execute([parsed[0]], 1, version) > ver_range_execute([parsed[2]], 1, version)
        elif parsed[1] == "<=":
            return ver_range_execute([parsed[0]], 1, version) <= ver_range_execute([parsed[2]], 1, version)
        elif parsed[1] == "<":
            return ver_range_execute([parsed[0]], 1, version) < ver_range_execute([parsed[2]], 1, version)
    if n == 4:
        return ver_range_execute(parsed[:2], 2, version) and ver_range_execute(parsed[2:], 2, version)
    if n == 5:
        if parsed[2] == "||":
            return ver_range_execute(parsed[:2], 2, version) or ver_range_execute(parsed[3:], 2, version)
    raise Exception((n, parsed))


xs = [r"([\*0-9a-zA-Z]+[\.\-])*[\*0-9a-zA-Z]+", "\s*(-|=|>=?|<=?|\|{2})\s*", "~>|~", "\^", "\s+"]


def get_sym(scanner, x):
    return x.strip()

scanner = re.Scanner([(x, get_sym) for x in xs])


def parse(expr):
    xs = scanner.scan(expr)
    if xs[1] != "":
        raise Exception((xs[0], xs[1]))
    return [x for x in xs[0] if x != '']


# print(SemverVersion("0.7.x") >= SemverVersion("0.7.0-asdf"))
# print(SemverVersion("0.7.0-addf") <= SemverVersion("0.7.x"))
