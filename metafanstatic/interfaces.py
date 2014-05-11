# -*- coding:utf-8 -*-
from zope.interface import Interface

class IListing(Interface):
    def iterate_search(word):
        pass

    def iterate_lookup(word):
        pass

    def iterate_versions(word):
        pass

class IDownloading(Interface):
    def download(url):
        pass

class ICreation(Interface):
    def create(zip_path):
        pass

class IExtracting(Interface):
    def extract(zip_path):
        pass

class IInformation(Interface):
    pass
