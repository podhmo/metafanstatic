# -*- coding:utf-8 -*-
from configless.interfaces import IPlugin
from .interfaces import IExtracting
from zope.interface import implementer
import os.path
import json
import zipfile
from .cache import JSONFileCache


@implementer(IExtracting, IPlugin)
class ExtractingFromZipfile(object):

    @classmethod
    def create_from_setting(cls, setting):
        return cls(
            setting["extracting.work.dirpath"],
            setting["extracting.cache.filename"],
        )

    def __init__(self, dirpath, cachename):
        self.cache = JSONFileCache.load(dirpath, os.path.join(dirpath, cachename))  # zippath -> bower.json
        self.work_dir = dirpath

    def extract(self, word, version, zippath):
        try:
            return self.cache[zippath]
        except KeyError:
            return self.cache.store(zippath, self.extract_bower_json_path(word, version, zippath))

    def extract_bower_json_path(self, word, version, zippath):
        if not zipfile.is_zipfile(zippath):
            raise Exception("not zipfile {}".format(zippath))
        zf = zipfile.ZipFile(zippath)
        bower_json_path = None
        for name in zf.namelist():
            if "bower.json" in name:
                bower_json_path = os.path.join(self.work_dir, name)
                break
        if bower_json_path is None:
            for name in zf.namelist():
                if "component.json" in name:
                    bower_json_path = os.path.join(self.work_dir, name)
                    break
        zf.extractall(self.work_dir)
        if bower_json_path is None:
            toplevel = os.path.split(zf.namelist()[0])[0]
            bower_json_path = os.path.join(self.work_dir, toplevel, "bower.json")
            with open(bower_json_path, "w") as wf:
                wf.write(json.dumps(fake_bower_json(word, version)))
            # raise RuntimeError("{} is not found in {}".format("bower.json", self.work_dir))
        return bower_json_path


def fake_bower_json(name, version):
    return {"name": name,
            "version": version,
            "main": "{}.js".format(name)}


def includeme(config):
    config.add_plugin("extracting", ExtractingFromZipfile)
