# -*- coding:utf-8 -*-
from zope.interface import (
    Interface,
    Attribute
)


class IListing(Interface):

    def iterate_search(word):
        pass

    def iterate_lookup(word):
        pass

    def iterate_versions(word):
        pass


class IDownloading(Interface):

    def download(url, version=None):
        pass


class ICreation(Interface):

    def create(zip_path):
        pass


class IExtracting(Interface):

    def extract(word, version, zip_path):
        pass


class IInformation(Interface):
    package = Attribute("package ame")
    # name = Attribute("")
    # dependencies = Attribute("")
    # version = Attribute("")
    # license = Attribute("")
