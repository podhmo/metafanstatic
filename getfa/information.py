# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from zope.interface import implementer
from .interfaces import IInformation, ICachedRequesting
from .decorator import reify
from .control import GithubAPIControl
from .cache import CachedRequesting


@implementer(IInformation)
class GithubInformation(object):
    tags_name = "github.tags"
    version_name = "github.version"
    rawfile_name = "github.rawfile"
    lookup_name = "heroku.lookup"
    search_name = "heroku.search"

    def __init__(self, app, control=GithubAPIControl()):
        self.app = app
        self.control = control

    @reify
    def lookup_requesting(self):
        return self.app.registry.getUtility(ICachedRequesting, name=self.lookup_name)

    @reify
    def version_requesting(self):
        return self.app.registry.getUtility(ICachedRequesting, name=self.version_name)

    @reify
    def search_requesting(self):
        return self.app.registry.getUtility(ICachedRequesting, name=self.search_name)

    @reify
    def tags_requesting(self):
        return self.app.registry.getUtility(ICachedRequesting, name=self.tags_name)

    @reify
    def rawfile_requesting(self):
        return self.app.registry.getUtility(ICachedRequesting, name=self.rawfile_name)

    def search(self, word):
        return self.search_requesting.get(word, self.control.on_search(word))

    def lookup(self, word):
        return self.lookup_requesting.get(word, self.control.on_lookup(word))

    def fullname(self, word):
        data = self.lookup(word)
        return self.control.fullname_of_url(data["url"])

    def version(self, word):
        try:
            val = self.version_requesting.cache[word]
            if hasattr(val, "get") and val.get("message", "").lower() == "not found":
                raise KeyError("not found")
            return val
        except KeyError:
            fullname = self.fullname(word)
            return self.version_requesting.get(word, self.control.on_versions(fullname))

    def remote_files(self, word, version):
        try:
            k = "{}@{}".format(word, version)
            return self.tags_requesting.cache[k]
        except KeyError:
            fullname = self.fullname(word)
            return self.tags_requesting.get(k, self.control.on_tags(fullname, version))

    def rawfile(self, word, version, path):
        try:
            k = "@".join([word, version, path])
            return self.rawfile_requesting.cache[k]
        except KeyError:
            fullname = self.fullname(word)
            return self.rawfile_requesting.get(k, self.control.on_rawfile(fullname, version, path))


def includeme(config):
    u = config.registry.registerUtility
    cachedir = config.registry.setting["cachedir"]

    name = GithubInformation.lookup_name
    u(CachedRequesting(cachedir, name, timelimit=60 * 5 * 10), ICachedRequesting, name=name)
    name = GithubInformation.version_name
    u(CachedRequesting(cachedir, name, timelimit=60 * 5 * 10), ICachedRequesting, name=name)

    name = GithubInformation.search_name
    u(CachedRequesting(cachedir, name, timelimit=60), ICachedRequesting, name=name)

    # tags
    name = GithubInformation.tags_name
    u(CachedRequesting(cachedir, name, timelimit=60 * 5 * 10), ICachedRequesting, name=name)
    name = GithubInformation.rawfile_name
    u(CachedRequesting(cachedir, name, timelimit=60 * 5 * 10 * 12), ICachedRequesting, name=name)

