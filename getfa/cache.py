# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import json
import os.path
import time

class ConflictCacheException(Exception):
    pass


class CacheItemNotFound(Exception):
    pass


class JSONCacheBase(object):
    @classmethod
    def clear_all(cls, storepath, cachepath):
        if os.path.exists(cachepath):
            os.remove(cachepath)

    @classmethod
    def clear(cls, storepath, cachepath, word):
        data = cls.load(storepath, cachepath)
        del data.cache[word]
        data.save()

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


class JSONDictCache(JSONCacheBase):
    def __init__(self, storepath, cachepath, cache, check=True, overwrite=True):
        self.storepath = storepath
        self.cachepath = cachepath
        self.cache = cache

        self.filecheck = check
        self.overwrite = overwrite

    def store(self, k, val):
        self.cache[k] = val
        self.save()
        return val

    def __getitem__(self, k):
        return self.cache[k]


class JSONFileCache(JSONCacheBase):
    def __init__(self, storepath, cachepath, cache, check=True, overwrite=True):
        self.storepath = storepath
        self.cachepath = cachepath
        self.cache = cache

        self.filecheck = check
        self.overwrite = overwrite

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


class TimelimitWrapper(object):
    def __init__(self, cache, expire_range=60 * 5):
        self.cache = cache
        self.expire_range = expire_range

    def __getitem__(self, k):
        (tm, val) = self.cache[k]
        tm = float(tm)
        if time.time() - tm > self.expire_range:
            raise KeyError("older {k}".format(k=k))
        return val

    def store(self, k, val):
        self.cache.store(k, (time.time(), val))
