# -*- coding:utf-8 -*-
from configless.interfaces import IPlugin
from .interfaces import IExtracting
from zope.interface import implementer
import requests
import os.path
from .cache import JSONFileCache
import zipfile

@implementer(IExtracting, IPlugin)
class ExtractingFromZipfile(object):
    @classmethod
    def create_from_setting(cls, setting):
        return cls(
            setting["extracting.work.dirpath"], 
            setting["extracting.cache.filename"],
        )

    def __init__(self, dirpath, cachename):
        self.cache = JSONFileCache.load(dirpath, os.path.join(dirpath, cachename)) #zippath -> bower.json
        self.work_dir = dirpath

    def extract(self, zippath):
        try:
            return self.cache[zippath]
        except KeyError:
            return self.cache.store(zippath, self.extract_bower_json_path(zippath))

    def extract_bower_json_path(self, zippath):
        if not zipfile.is_zipfile(zippath):
            raise Exception("not zipfile {}".format(zippath))
        zf = zipfile.ZipFile(zippath)

        for name in zf.namelist():
            if "bower.json" in name:
                bower_json_path = os.path.join(self.work_dir, name)
        zf.extractall(self.work_dir)
        return bower_json_path

def includeme(config):
    config.add_plugin("extracting", ExtractingFromZipfile)



