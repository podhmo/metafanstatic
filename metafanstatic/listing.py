# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from configless.interfaces import IPlugin
from .interfaces import IListing
from zope.interface import implementer
import requests
import os
import re

github_rx = re.compile(r"git://github\.com/(\S+)\.git$")


def repository_url_to_tag_json_url(url):
    m = github_rx.search(url)
    if m:
        return "https://api.github.com/repos/{name}/git/refs/tags".format(name=m.group(1))
    raise NotImplementedError(url)


@implementer(IListing, IPlugin)
class Listing(object):

    @classmethod
    def create_from_setting(cls, setting):
        return cls(
            setting["listing.search.url"],
            setting["listing.lookup.url"],
        )

    def __init__(self, search_url, lookup_url):
        self.search_url = search_url
        self.lookup_url = lookup_url

    def iterate_lookup(self, word):
        url = os.path.join(self.lookup_url, word)
        logger.debug("lookup: %s", url)
        yield requests.get(url).json()

    def iterate_search(self, word):
        url = os.path.join(self.search_url, word)
        logger.debug("search: %s", url)
        for val in requests.get(url).json():
            yield val

    def iterate_versions(self, word):
        data = next(self.iterate_lookup(word))
        url = data["url"]
        tag_json_url = repository_url_to_tag_json_url(url)
        logger.debug("versions: %s", tag_json_url)
        for val in requests.get(tag_json_url).json():
            yield data["url"], val


def includeme(config):
    config.add_plugin("listing", Listing)
