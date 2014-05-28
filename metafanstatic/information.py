# -*- coding:utf-8 -*-
import logging
import requests
import os.path
logger = logging.getLogger(__name__)
from zope.interface import implementer
from metafanstatic.interfaces import IInformation
from .utils import safe_json_load
from .urls import get_repository_fullname_from_url


def repository_url_to_github_trees_url(url, version):
    name = get_repository_fullname_from_url(url)
    if name is None:
        raise NotImplementedError(url)
    trees_url = "https://api.github.com/repos/{name}/git/trees/{sha}".format(name=name, sha=version)
    #trees_url = "https://api.github.com/repos/{name}/git/trees/{sha}?recursive=1".format(name=name, sha=version)
    return trees_url


def repository_url_to_github_raw_url(url, version, filepath):
    name = get_repository_fullname_from_url(url)
    if name is None:
        raise NotImplementedError(url)
    fmt = "https://raw.githubusercontent.com/{name}/{version}/{filepath}"
    raw_url = fmt.format(name=name, version=version, filepath=filepath)
    return raw_url


def fake_bower_json_from_repository_url(url, version):
    fullname = get_repository_fullname_from_url(url)
    name = fullname.split("/")[-1]
    return {"name": name,
            "version": version,
            "main": "{}.js".format(name)}


class BaseInformation(object):
    @property
    def package(self):
        return "meta.js.{}".format(self.bower_json["name"])

    @property
    def name(self):
        return self.bower_json["name"]

    @property
    def license(self):
        return self.bower_json.get("license", "-")

    @property
    def description(self):
        return self.bower_json.get("description", "-")

    @property
    def dependencies(self):
        r = []
        for name, raw_version in self.bower_json.get("dependencies", {}).items():
            if raw_version == "":
                version = "master"  # xxx:
            elif raw_version.startswith("~"):  # xxx:
                version = raw_version.lstrip("~")
            else:
                version = "master"  # xxxx:
            # elif raw_version.startswith(("<", ">")):
            #     version = version.lstrip("<=>")  # xxx:
            r.append({"name": name, "version": version, "raw_expression": raw_version})
        return r


# see: metafanstatic.interfaces:IInformation
@implementer(IInformation)
class RemoteInformation(BaseInformation):
    target_file = "bower.json"

    @classmethod
    def create_from_setting(cls, setting, url, version):
        trees_url = repository_url_to_github_trees_url(url, version)
        raw_url = repository_url_to_github_raw_url(url, version, cls.target_file)
        return cls(url, version, trees_url=trees_url, raw_url=raw_url)

    def __init__(self, url, version, trees_url, raw_url):
        self.url = url
        self.version = version
        self.trees_url = trees_url
        self.raw_url = raw_url
        self.bower_json = self.get_information()

    @property
    def name(self):
        try:
            return self.bower_json["name"]
        except KeyError:
            return get_repository_fullname_from_url(self.url)

    def iterate_trees(self):
        logger.info("loading:%s", self.trees_url)
        response = requests.get(self.trees_url).json()
        for data in response.get("tree", []):
            yield data

    def get_information(self):
        for data in self.iterate_trees():
            if data["path"].endswith(self.target_file):
                logger.info("loading:%s", self.raw_url)
                return requests.get(self.raw_url).json()
        logger.warn("{} is not found in {}".format(self.target_file, self.trees_url))
        return fake_bower_json_from_repository_url(self.url, self.version)


@implementer(IInformation)
class Information(BaseInformation):
    @classmethod
    def create_from_setting(cls, setting, bower_file_path, version):
        return cls(bower_file_path, version)

    def __init__(self, bower_file_path, version):
        self.version = version
        self.bower_file_path = bower_file_path
        self.bower_dir_path = os.path.dirname(self.bower_file_path)
        self.bower_json = safe_json_load(bower_file_path)

    def push_data(self, input):
        input.update(self.bower_json)
        input.update(dict(package=self.package,
                          dependencies=self.bower_json.get("dependencies", []),
                          bower_dir_path=self.bower_dir_path,
                          name=self.bower_json.get("name", "").replace("-", "_"),
                          description=self.description,
                          main_js_path_list=self.main_js_path_list))


def includeme(config):
    config.add_plugin("information", Information)
    config.add_plugin("information:remote", RemoteInformation)
