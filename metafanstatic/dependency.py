# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import os.path
from .classifier import RequestType
from miniadt import dispatchmethod


class GithubDependencyCollector(object):
    def __init__(self, app, information, detector, classifier):
        self.app = app
        self.information = information
        self.detector = detector
        self.classifier = classifier

    def one_dependency(self, word, restriction=""):
        version = self.detector.choose_version(self.information, word, restriction)
        taglist = self.information.remote_files(word, version)
        result = self.information.rawfile(word, version, self.detector.anything_json_path(taglist))
        return result

    def recursive_dependency(self, word, restriction=""):
        result = {}
        request = self.classifier.classified_request(word, restriction)
        self._recursive_dependency(request, {}, result)
        return result

    def _recursive_dependency(self, request, history, result):
        if request.name in history:
            return
        history[request.name] = 1

        parent_dict = get_dependency(request, self)
        parent_name = parent_dict["name"]
        result[parent_name] = parent_dict

        for subname, subrestriction in parent_dict.get("dependencies", {}).items():
            request = self.classifier.classified_request(subname, subrestriction)
            self._recursive_dependency(request, history, result)


@RequestType.match_method
class get_dependency(object):
    def __init__(self, dependency_collector):
        self.dependency_collector = dependency_collector

    @dispatchmethod
    def URLRequest(self, name, url):
        return {"name": name,
                "rawurl": url,
                "version": None,
                "main": os.path.basename(url)}

    @dispatchmethod
    def VersionRequest(self, name, version, restriction):
        return self.dependency_collector.one_dependency(name, restriction)
