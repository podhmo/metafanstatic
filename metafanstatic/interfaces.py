# -*- coding:utf-8 -*-
from zope.interface import Interface

class IListing(Interface):
    def iterate_repository(word):
        pass

class IDownloading(Interface):
    def download(url):
        pass

class ICreation(Interface):
    def create(zip_path):
        pass

