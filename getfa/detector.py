# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from semver import max_satisfying


class NotFound(Exception):
    pass


class GithubDetector(object):
    def __init__(self, app):
        self.app = app

    def choose_version(self, information, word, restriction=""):
        versions = [d["name"] for d in information.version(word)]
        return max_satisfying(versions, restriction, loose=True)

    def anything_json_path(self, taglist):
        try:
            return self.bower_json_path(taglist)
        except NotFound:
            return self.component_json_path(taglist)

    def bower_json_path(self, taglist):
        for line in taglist["tree"]:
            if line["path"] == "bower.json":
                return line["path"]
        raise NotFound("bower.json")

    def component_json_path(self, taglist):
        for line in taglist["tree"]:
            if line["path"] == "component.json":
                return line["path"]
        raise NotFound("component.json")
