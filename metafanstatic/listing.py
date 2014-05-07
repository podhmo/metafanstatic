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
        return cls(setting["listing.search.url"])

    def __init__(self, url):
        self.url = url

    def iterate_repository(self, word):
        url = os.path.join(self.url, word)
        for val in requests.get(url).json():
            yield val

def includeme(config):
    config.add_plugin("listing", Listing)
