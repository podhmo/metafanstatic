# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from zope.interface import implementer
import json
import requests
import zipfile
import os.path
from .interfaces import IDownloading, ICachedRequesting, ICache
from .decorator import reify
from .control import GithubAPIControl
from .cache import CachedStreamRequesting, JSONFileCache, _FileStreamAdapter


class NotZipFile(Exception):
    pass


def zip_extracting(zippath, dst):
    if not zipfile.is_zipfile(zippath):
        raise NotZipFile(zippath)
    zf = zipfile.ZipFile(zippath)
    zf.extractall(dst)
    toplevel = os.path.split(zf.namelist()[0])[0]
    return os.path.join(dst, toplevel)


def fake_bower_package(dirname, filename, dst):
    dirpath = os.path.join(dst, dirname)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    params = {
        "name": dirname,
        "version": "",
        "main": [filename]
    }
    with open(os.path.join(dirpath, "bower.json"), "w") as wf:
        wf.write(json.dumps(params))
    return dirpath


@implementer(IDownloading)
class RawDownloading(object):
    def __init__(self, app):
        self.app = app

    def download(self, url, dst, name=None):
        logger.info("loading: %s", url)
        filestream = _FileStreamAdapter(url, requests.get(url, stream=True))
        dirpath = fake_bower_package((name or filestream.name), filestream.name, dst)
        with open(os.path.join(dirpath, filestream.name), "wb") as wf:
            for chunk in filestream:
                wf.write(chunk)


@implementer(IDownloading)
class GithubDownloading(object):
    download_name = "github.zip"
    workdir_name = "github.workdir.zip"

    def __init__(self, app, information, control=GithubAPIControl(), extracting=zip_extracting):
        self.app = app
        self.information = information
        self.control = control
        self.extracting = zip_extracting

    @reify
    def download_requesting(self):
        return self.app.registry.getUtility(ICachedRequesting, name=self.download_name)

    @reify
    def workdir_cache(self):
        return self.app.registry.getUtility(ICache, name=self.workdir_name)

    def zip_download(self, word, version):
        k = "@".join((word, str(version)))
        try:
            val = self.download_requesting.cache[k]
            return val
        except KeyError:
            fullname = self.information.fullname(word)
            return self.download_requesting.get(k, self.control.on_download(fullname, version))

    def download(self, word, dst, version=None):
        k = "@".join((word, str(version)))
        try:
            return self.workdir_cache[k]
        except KeyError:
            zip_path = self.zip_download(word, version)
            try:
                return self.extracting(zip_path, dst)
            except NotZipFile:
                self.download_requesting.clear(k)
                raise


def includeme(config):
    u = config.registry.registerUtility
    cachedir = config.registry.setting["cachedir"]

    name = GithubDownloading.download_name
    u(CachedStreamRequesting(cachedir, name), ICachedRequesting, name=name)

    name = GithubDownloading.workdir_name
    u(JSONFileCache.load(cachedir, name), ICache, name=name)
