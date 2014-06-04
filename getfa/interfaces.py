# -*- coding:utf-8 -*-
from zope.interface import Interface


class IInformation(Interface):
    def lookup(word):
        pass

    def search(word):
        pass

    def versions(word):
        pass

    def dependency(word):
        pass


class IDownloading(Interface):
    def download(word, dst):
        pass


class ICachedRequesting(Interface):
    def get(word, url):
        pass

    def clear(word):
        pass


class ICache(Interface):
    def clear(storepath, cachepath, word):
        pass

    def load(storepath, cachepath):
        pass

    def store(k, path):
        pass

    def __getitem__(k, path):
        pass
