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
    version_name = "github.version"
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


def includeme(config):
    u = config.registry.registerUtility
    cachedir = config.registry.setting["cachedir"]

    name = GithubInformation.lookup_name
    u(CachedRequesting(cachedir, name, timelimit=60 * 5), ICachedRequesting, name=name)
    name = GithubInformation.version_name
    u(CachedRequesting(cachedir, name, timelimit=60 * 5), ICachedRequesting, name=name)

    name = GithubInformation.search_name
    u(CachedRequesting(cachedir, name, timelimit=60), ICachedRequesting, name=name)
