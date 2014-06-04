# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import json
import os.path
import time
import requests
from zope.interface import implementer
from .interfaces import ICachedRequesting, ICache
from .decorator import reify


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
        data.cache.pop(word, None)
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


@implementer(ICache)
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


@implementer(ICache)
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


@implementer(ICachedRequesting)
class CachedRequesting(object):
    def __init__(self, cachedir, cachename, cacheclass=JSONDictCache, timelimit=None):
        self.cachedir = cachedir
        self.cachename = cachename
        self.cacheclass = cacheclass
        self.timelimit = timelimit

    @reify
    def cache_path(self):
        return os.path.join(self.cachedir, "cache.{}.json".format(self.cachename))

    @reify
    def cache(self):
        if self.timelimit:
            return TimelimitWrapper(self.cacheclass.load(self.cachedir, self.cache_path), self.timelimit)
        else:
            return self.cacheclass.load(self.cachedir, self.cache_path)

    def clear(self, word):
        logger.info("clear: word=%s", word)
        return self.cacheclass.clear(self.cachedir, self.cache_path, word)

    def clear_all(self):
        logger.info("clear all: %s", self.cache_path)
        return self.cacheclass.clear_all(self.cachedir, self.cache_path)

    def get(self, word, url):
        logger.info("loading: word=%s, %s", word, url)
        try:
            return self.cache[word]
        except KeyError:
            response = requests.get(url).json()
            self.cache.store(word, response)
            return response


@implementer(ICachedRequesting)
class CachedStreamRequesting(object):
    def __init__(self, cachedir, cachename, cacheclass=JSONFileCache, timelimit=None):
        self.cachedir = cachedir
        self.cachename = cachename
        self.cacheclass = cacheclass
        self.timelimit = timelimit

    @reify
    def cache_path(self):
        return os.path.join(self.cachedir, "cache.{}.json".format(self.cachename))

    @reify
    def cache(self):
        if self.timelimit:
            return TimelimitWrapper(self.cacheclass.load(self.cachedir, self.cache_path), self.timelimit)
        else:
            return self.cacheclass.load(self.cachedir, self.cache_path)

    def clear(self, word):
        logger.info("clear: word=%s", word)
        return self.cacheclass.clear(self.cachedir, self.cache_path, word)

    def clear_all(self):
        logger.info("clear all: %s", self.cache_path)
        return self.cacheclass.clear_all(self.cachedir, self.cache_path)

    def get(self, word, url):
        logger.info("loading: word=%s, %s", word, url)
        try:
            return self.cache[word]
        except KeyError:
            response = requests.get(url, stream=True)
            return self.cache.store_stream(word, _FileStreamAdapter(url, response))


class _FileStreamAdapter(object):
    def __init__(self, url, requests_stream, chunk_size=8 * 1024):
        self.url = url
        self.requests_stream = requests_stream
        self.chunk_size = chunk_size
        self.stream = None

    @property
    def name(self):
        disposition = self.requests_stream.headers.get("content-disposition")
        if disposition:
            return disposition.split("=")[1]
        else:
            return os.path.basename(self.url)

    def __iter__(self):
        return self.requests_stream.iter_content(chunk_size=self.chunk_size)
