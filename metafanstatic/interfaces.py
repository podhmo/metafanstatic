# -*- coding:utf-8 -*-
from zope.interface import Interface

class IListing(Interface):
    def iterate_repository(word):
        pass
