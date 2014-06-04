# -*- coding:utf-8 -*-
from miniadt import ADTTypeProvider
RequestType = ADTTypeProvider("Request")

URLRequet = RequestType("URLRequest", "name url")
VersionRequest = RequestType("VersionRequest", "name version restriction")


class GithubClassifier(object):
    def __init__(self, app):
        self.app = app

    def classified_request(self, name, dependency):
        if any(dependency.startswith(x) for x in ("http://", "https://")):
            return URLRequet(name=name, url=dependency)
        else:
            return VersionRequest(name=name, version=None, restriction=dependency)
