# -*- coding:utf-8 -*-
import logging
import os.path
logger = logging.getLogger(__name__)
import json
from zope.interface import implementer
from metafanstatic.interfaces import IInformation

# see: metafanstatic.interfaces:IInformation


@implementer(IInformation)
class Information(object):

    @classmethod
    def create_from_setting(cls, setting, bower_file_path):
        return cls(bower_file_path)

    def __init__(self, bower_file_path):
        self.bower_file_path = bower_file_path
        self.bower_dir_path = os.path.dirname(self.bower_file_path)
        with open(bower_file_path, "r") as rf:
            self.data = json.load(rf)

    @property
    def package(self):
        return "meta.js.{}".format(self.data["name"])

    @property
    def description(self):
        return self.data.get("description", "-")

    @property
    def main_js_path_list(self):
        if isinstance(self.data["main"], (list, tuple)):
            main_list = self.data["main"]
        else:
            main_list = [self.data["main"]]
        return [os.path.join(self.bower_dir_path, m) for m in main_list]

    @property
    def min_js_path_list(self):
        return [m[:-3] + ".min.js" for m in self.main_js_path_list]

    def exists_info(self):
        return {
            "main_js_list": {m: os.path.exists(m) for m in self.main_js_path_list},
        }

    @property
    def dependencies(self):
        return self.data.get("dependencies", [])

    def push_data(self, input):
        input.update(self.data)
        input.update(dict(package=self.package,
                          bower_dir_path=self.bower_dir_path,
                          name=self.data.get("name", "").replace("-", "_"),
                          description=self.description,
                          main_js_path_list=self.main_js_path_list))


def includeme(config):
    config.add_plugin("information", Information)
