# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import os.path
import json


def find_target_from_candidates(root, targets):
    for f in targets:
        path = os.path.join(root, f)
        if os.path.exists(path):
            return path
    raise Exception("{path} is not found".format(path=path))


def load_from_file(filename):
    with open(filename, "r") as rf:
        return json.load(rf)


class Loader(object):
    def __init__(self,
                 finder=find_target_from_candidates,
                 loader=load_from_file,
                 targets=["bower.json", "complement.json"]):
        self.finder = finder
        self.loader = loader
        self.targets = targets

    def find_target(self, root):
        return self.finder(root, self.targets)

    def load_from_target(self, path):
        logger.info("loading: %s", path)
        return self.loader(path)

    def load(self, root):
        path = self.find_target(root)
        data = self.load_from_target(path)
        data["bower_directory"] = os.path.dirname(path)
        return data

