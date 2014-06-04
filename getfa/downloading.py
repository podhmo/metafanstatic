# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from zope.interface import implementer
import zipfile
import os.path
from .interfaces import IDownloading, ICachedRequesting, ICache
from .decorator import reify
from .control import GithubAPIControl
from .cache import CachedStreamRequesting, JSONFileCache


def zip_extracting(zippath, dst):
    if not zipfile.is_zipfile(zippath):
        raise Exception("not zipfile {}".format(zippath))
    zf = zipfile.ZipFile(zippath)
    zf.extractall(dst)
    toplevel = os.path.split(zf.namelist()[0])[0]
    return os.path.join(dst, toplevel)


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
        k = "@".join((word, repr(version)))
        try:
            val = self.download_requesting.cache[k]
            return val
        except KeyError:
            fullname = self.information.fullname(word)
            return self.download_requesting.get(k, self.control.on_download(fullname, version))

    def download(self, word, version, dst):
        k = "@".join((word, repr(version)))
        try:
            return self.workdir_cache[k]
        except KeyError:
            zip_path = self.zip_download(word, version)
            return self.extracting(zip_path, dst)


def includeme(config):
    u = config.registry.registerUtility
    cachedir = config.registry.setting["cachedir"]

    name = GithubDownloading.download_name
    u(CachedStreamRequesting(cachedir, name), ICachedRequesting, name=name)

    name = GithubDownloading.workdir_name
    u(JSONFileCache.load(cachedir, name), ICache, name=name)
