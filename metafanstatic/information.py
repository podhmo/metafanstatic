# -*- coding:utf-8 -*-
import logging
import requests
import os.path
logger = logging.getLogger(__name__)
from zope.interface import implementer
from metafanstatic.interfaces import IInformation
from .utils import safe_json_load, reify
from .urls import get_repository_fullname_from_url
from .cache import JSONDictCache


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
            r.append({"name": name, "version": raw_version})
        return r


# see: metafanstatic.interfaces:IInformation
@implementer(IInformation)
class RemoteInformation(BaseInformation):
    target_file = "bower.json"

    @classmethod
    def create_from_setting(cls, setting, url, version):
        trees_url = repository_url_to_github_trees_url(url, version)
        raw_url = repository_url_to_github_raw_url(url, version, cls.target_file)
        return cls(url, version, trees_url=trees_url, raw_url=raw_url,
                   cachedir=setting["information.cache.dirpath"],
                   trees_cache_name=setting["information.cache.trees.filename"],
                   raw_cache_name=setting["information.cache.bower.filename"])

    def __init__(self, url, version, trees_url, raw_url, cachedir, trees_cache_name, raw_cache_name):
        self.url = url
        self.version = version
        self.trees_url = trees_url
        self.raw_url = raw_url
        self.cachedir = cachedir
        self.trees_cache_name = trees_cache_name
        self.raw_cache_name = raw_cache_name
        self.bower_json = self.get_information()

    @property
    def name(self):
        try:
            return self.bower_json["name"]
        except KeyError:
            return get_repository_fullname_from_url(self.url)

    @reify
    def trees_cache(self):
        dirpath = self.cachedir
        cachename = self.trees_cache_name
        return JSONDictCache.load(dirpath, os.path.join(dirpath, cachename))  # url -> trees

    @reify
    def raw_cache(self):
        dirpath = self.cachedir
        cachename = self.raw_cache_name
        return JSONDictCache.load(dirpath, os.path.join(dirpath, cachename))  # url -> raw

    def iterate_trees(self):
        try:
            for data in self.trees_cache[self.trees_url]:
                yield data
        except KeyError:
            logger.info("loading:%s", self.trees_url)
            response = requests.get(self.trees_url).json()
            self.trees_cache.store(self.trees_url, list(response.get("tree", [])))
            for data in response.get("tree", []):
                yield data

    def get_information(self):
        for data in self.iterate_trees():
            if data["path"].endswith(self.target_file):
                try:
                    return self.raw_cache[self.raw_url]
                except KeyError:
                    logger.info("loading:%s", self.raw_url)
                    response = requests.get(self.raw_url).json()
                    self.raw_cache.store(self.raw_url, response)
                    return response
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

    @reify
    def main_js_path_list(self):
        main = self.bower_json["main"]
        if isinstance(main, (list, tuple)):
            main_files = main
        else:
            main_files = [main]
        return [os.path.join(self.bower_dir_path, f) for f in main_files]

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
