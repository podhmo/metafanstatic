# -*- coding:utf-8 -*-
import re
import shutil
import os.path
import logging
logger = logging.getLogger(__name__)

from .compat import FileNotFoundError

junk_prefix = re.compile(r'^/\./|^\./')
js_sufix = re.compile(r'\.js$')


class JSResourceIterator(object):

    def __init__(self, basepath, files, dst):
        self.basepath = basepath
        self.files = files
        self.dst = dst

    def copyfiles(self, filepath, filename):
        if not filename:
            return
        dst = os.path.join(self.dst, filename)
        logger.debug("copy file: %s -> %s", filepath, dst)
        try:
            shutil.copy2(filepath, dst)
        except FileNotFoundError as e:
            if os.path.exists(os.path.dirname(dst)):
                raise e
            os.makedirs(os.path.dirname(dst))
            shutil.copy2(filepath, dst)

    def __iter__(self):
        for f in self.files:
            if not os.path.exists(f):
                logger.warn("{} is not found".format(f))
                continue
            if os.path.isdir(f):
                logger.warn("{} is directory".format(f))
                continue

            filename = flatten_filename(self.basepath, f)
            minified_path = minified_name(f)
            if os.path.exists(minified_path):
                minified = flatten_filename(self.basepath, minified_path)
            else:
                minified = False
            if filename == minified:
                minified = False
            # xxxx:
            self.copyfiles(f, filename)
            self.copyfiles(minified_path, minified)

            ext = os.path.splitext(filename)[1]

            if any(ext.endswith(x) for x in [".css", ".js"]):
                yield namenize(filename), filename, minified


def flatten_filename(root, js_file):
    flattend = js_file.replace(root, "", 1)
    return junk_prefix.sub("", flattend).lstrip("/")


def minified_name(name):
    return js_sufix.sub(".min.js", name)


def namenize(filename):
    name = os.path.basename(filename)
    if name[0].isdigit():
        name = "_" + name
    return name.replace(".", "_").replace("-", "_")

import pprint


def dict_print(D):
    return pprint.pformat(D, indent=2, width=120)
