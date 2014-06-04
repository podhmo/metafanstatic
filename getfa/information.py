# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import os.path
import requests
from zope.interface import implementer
from .interfaces import IInformation, ICachedRequesting
from .cache import JSONDictCache, TimelimitWrapper
from .decorator import reify

import re
github_rx = re.compile(r"git://github\.com/(\S+)(?:\.git)?$")


def get_repository_fullname_from_url(url):
    """ repository_fullname = :owener/:name"""
    m = github_rx.search(url)
    if m:
        return m.group(1).replace(".git", "")
    return None


class GithubAPIControl(object):
    def on_versions(self, fullname):  # fullname = :author:/:package:
        if fullname:
            return "https://api.github.com/repos/{name}/tags".format(name=fullname)
        raise NotImplementedError(fullname)

    def on_lookup(self, word=""):
        return "https://bower.herokuapp.com/packages/{}".format(word)


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

    def get(self, word, url):
        logger.info("loading: word=%s, %s", word, url)
        try:
            return self.cache[word]
        except KeyError:
            response = requests.get(url).json()
            self.cache.store(word, response)
            return response


@implementer(IInformation)
class GithubInformation(object):
    version_name = "github.version"
    lookup_name = "heroku.lookup"

    def __init__(self, app, control=GithubAPIControl()):
        self.app = app
        self.control = control

    @reify
    def lookup_requesting(self):
        return self.app.registry.getUtility(ICachedRequesting, name=self.lookup_name)

    @reify
    def version_requesting(self):
        return self.app.registry.getUtility(ICachedRequesting, name=self.version_name)

    def lookup(self, word):
        return self.lookup_requesting.get(word, self.control.on_lookup(word))

    def fullname(self, word):
        data = self.lookup(word)
        return get_repository_fullname_from_url(data["url"])

    def version(self, word):
        try:
            val = self.version_requesting.cache[word]
            if hasattr(val, "get") and val.get("message", "").lower() == "not found":
                raise KeyError("not found")
            return val
        except KeyError:
            fullname = self.fullname(word)
            return self.version_requesting.get(word, self.control.on_versions(fullname))


def includeme(config):
    u = config.registry.registerUtility
    cachedir = config.registry.setting["cachedir"]

    name = GithubInformation.lookup_name
    u(CachedRequesting(cachedir, name, timelimit=60 * 5), ICachedRequesting, name=name)
    name = GithubInformation.version_name
    u(CachedRequesting(cachedir, name, timelimit=60 * 5), ICachedRequesting, name=name)
