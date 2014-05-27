# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from configless.interfaces import IPlugin
from .interfaces import IListing
from zope.interface import implementer
import requests
import os
import time
from .utils import reify
from .cache import JSONDictCache
from .urls import get_repository_fullname_from_url


def repository_url_to_tag_json_url(url):
    name = get_repository_fullname_from_url(url)
    if name:
        return "https://api.github.com/repos/{name}/git/refs/tags".format(name=name)
    raise NotImplementedError(url)


@implementer(IListing, IPlugin)
class Listing(object):

    @classmethod
    def create_from_setting(cls, setting):
        return cls(
            setting["listing.search.url"],
            setting["listing.lookup.url"],
            setting["listing.cache.dirpath"],
            setting["listing.cache.url.filename"],
            setting["listing.cache.versions.filename"]
        )

    def __init__(self, search_url, lookup_url, cachedir, url_cache_name, versions_cache_name):
        self.search_url = search_url
        self.lookup_url = lookup_url
        self.cachedir = cachedir
        self.url_cache_name = url_cache_name
        self.versions_cache_name = versions_cache_name

    @reify
    def url_cache(self):
        dirpath = self.cachedir
        cachename = self.url_cache_name
        return JSONDictCache.load(dirpath, os.path.join(dirpath, cachename))  # word -> url

    @reify
    def versions_cache(self):
        dirpath = self.cachedir
        cachename = self.versions_cache_name
        return JSONDictCache.load(dirpath, os.path.join(dirpath, cachename))  # word -> versions

    EXPIRE_RANGE = 60 * 5

    def iterate_lookup(self, word):
        try:
            (tm, url) = self.url_cache[word]
            tm = float(tm)
            if time.time() - tm > self.EXPIRE_RANGE:
                raise KeyError("older")
            return [url]
        except KeyError:
            url = os.path.join(self.lookup_url, word)
            logger.debug("lookup: %s", url)
            try:
                result = requests.get(url).json()
                self.url_cache.store(word, (time.time(), result))
                return [result]
            except ValueError:
                logger.info("matched repository not found. word=%s", word)
                return []

    def iterate_search(self, word):
        url = os.path.join(self.search_url, word)
        logger.debug("search: %s", url)
        for val in requests.get(url).json():
            yield val

    def iterate_versions(self, word, url=None):
        if url is None:
            urls = self.iterate_lookup(word)
            if not urls:
                return []
            data = next(iter(urls))
            url = data["url"]
        try:
            (tm, versions) = self.versions_cache[word]
            tm = float(tm)
            if time.time() - tm > self.EXPIRE_RANGE:
                raise KeyError("older")
            return versions
        except KeyError:
            tag_json_url = repository_url_to_tag_json_url(url)
            logger.debug("versions: %s", tag_json_url)
            url_version_pair_list = [(url, val) for val in requests.get(tag_json_url).json()]
            self.versions_cache.store(word, (time.time(), url_version_pair_list))
            return url_version_pair_list


def includeme(config):
    config.add_plugin("listing", Listing)
