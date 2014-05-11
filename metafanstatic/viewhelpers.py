# -*- coding:utf-8 -*-
import re
import shutil
import os.path
import logging
logger = logging.getLogger(__name__)

junk_prefix = re.compile(r'^/\./|^\./')
js_sufix = re.compile(r'\.js$')

class JSResourceIterator(object):
    def __init__(self, basepath, files, dst):
        self.basepath = basepath
        self.files = files
        self.dst = dst

    def copyfiles(self, filepath, filename):
        if filename:
            dst = os.path.join(self.dst, filename)
            logger.debug("copy file: %s -> %s", filepath, dst)
            shutil.copy2(filepath, dst)

    def __iter__(self):
        for f in self.files:
            if not os.path.exists(f):
                raise Exception("{} is not found".format(f))
            filename = flatten_filename(self.basepath, f)
            minified_path = minified_name(f)
            if os.path.exists(minified_path):
                minified = flatten_filename(self.basepath, minified_path)
            else:
                minified = False
            ##xxxx:
            self.copyfiles(f, filename)
            self.copyfiles(minified_path, minified)

            yield namenize(filename), filename, minified

def flatten_filename(root, js_file):
    flattend = js_file.replace(root, "")
    return junk_prefix.sub("", flattend)

def minified_name(name):
    return js_sufix.sub(".min.js", name)

def namenize(filename):
    return filename.replace(".", "_")

import pprint

def dict_print(D):
    return pprint.pformat(D, indent=2, width=120)

