# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import json
import os.path


class ConflictCacheException(Exception):
    pass


class CacheItemNotFound(Exception):
    pass


class JSONFileCache(object):

    def __init__(self, storepath, cachepath, cache, check=True, overwrite=True):
        self.storepath = storepath
        self.cachepath = cachepath
        self.cache = cache

        self.filecheck = check
        self.overwrite = overwrite

    @classmethod
    def load(cls, storepath, cachepath, check=True):
        if not os.path.exists(storepath):
            os.makedirs(storepath)

        if not os.path.exists(cachepath):
            return cls(storepath, cachepath, {}, check=check)
        else:
            with open(cachepath, "r") as rf:
                return cls(storepath, cachepath, json.load(rf), check=check)

    def save(self):
        dirpath = os.path.dirname(self.cachepath)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        with open(self.cachepath, "w") as wf:
            wf.write(json.dumps(self.cache))

    def store_stream(self, k, filestream):
        path = os.path.join(self.storepath, filestream.name)
        if not self.overwrite and os.path.exists(path):
            raise ConflictCacheException(path)

        with open(path, "wb") as wf:
            for chunk in filestream:
                wf.write(chunk)
        self.cache[k] = path
        self.save()
        return path

    def store(self, k, path):
        if not os.path.isabs(path):
            path = self.os.path.join(self.store, path)
        if not os.path.exists(path):
            raise CacheItemNotFound(path)
        self.cache[k] = path
        self.save()
        return path

    def __getitem__(self, k):
        path = self.cache[k]
        if self.filecheck and not os.path.exists(path):
            raise ConflictCacheException(path)
        return path
