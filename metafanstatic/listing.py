# -*- coding:utf-8 -*-
from configless.interfaces import IPlugin
from .interfaces import IListing
from zope.interface import implementer
import requests
import os

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
        yield requests.get(url).json()

    def iterate_search(self, word):
        url = os.path.join(self.search_url, word)
        for val in requests.get(url).json():
            yield val

def includeme(config):
    config.add_plugin("listing", Listing)
