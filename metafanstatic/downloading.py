# -*- coding:utf-8 -*-
from configless.interfaces import IPlugin
from .interfaces import IDownloading
from zope.interface import implementer
import re
import json
import requests
import os.path

class ConflictCacheException(Exception):
    pass

class JSONFileCache(object):
    def __init__(self, storepath, cachepath, cache, check=True, overwrite=True):
        self.storepath = storepath
        self.cachepath = cachepath
        self.cache = cache

        self.filecheck = check
        self.overwrite = overwrite

    @classmethod
    def load(cls, storepath, cachepath, check=True):
        if not os.path.exists(storepath):
            os.makedirs(storepath)

        if not os.path.exists(cachepath):
            return cls(storepath, cachepath, {}, check=check)
        else:
            with open(cachepath, "r") as rf:
                return cls(storepath, cachepath, json.load(rf), check=check)

    def save(self):
        dirpath = os.path.dirname(self.cachepath)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        with open(self.cachepath, "w") as wf:
            wf.write(json.dumps(self.cache))


    def __setitem__(self, k, filestream):
        path = os.path.join(self.storepath, filestream.name)
        if not self.overwrite and os.path.exists(path):
            raise ConflictCacheException(path)

        with open(path, "wb") as wf:
            for chunk in filestream:
                wf.write(chunk)
        self.cache[k] = path
        self.save()

    def __getitem__(self, k):
        path = self.cache[k]
        if self.filecheck and not os.path.exists(path):
            raise ConflictCacheException(path)
        return path

class _FileStreamAdapter(object):
    def __init__(self, url, requests_stream, chunk_size=8*1024):
        self.url = url
        self.requests_stream = requests_stream
        self.chunk_size = chunk_size
        self.stream = None

    @property
    def name(self):
        disposition = self.requests_stream.headers.get("content-disposition")
        if disposition:
            return disposition.split("=")[1]
        else:
            return os.path.basename(self.url)

    def __iter__(self):
        return self.requests_stream.iter_content(chunk_size=self.chunk_size)


github_rx = re.compile(r"git://github\.com/(\S+)\.git$")
def repository_url_to_download_zip_url(url):
    m = github_rx.search(url)
    if m:
        return "https://github.com/{name}/archive/master.zip".format(name=m.group(1))
    raise NotImplementedError(url)

@implementer(IDownloading, IPlugin)
class DownloadingFromRepositoryURI(object):
    @classmethod
    def create_from_setting(cls, setting):
        return cls(
            setting["download.cache.dirpath"], 
            setting["download.cache.filename"], 
            to_download_url=repository_url_to_download_zip_url
        )

    def __init__(self, dirpath, cachename, to_download_url):
        self.cache = JSONFileCache.load(dirpath, os.path.join(dirpath, cachename))
        self.cache_dir = dirpath
        self.to_download_url = to_download_url

    def download(self, url):
        zip_url = self.to_download_url(url)
        try:
            return self.cache[zip_url]
        except KeyError:
            self.cache[zip_url] = _FileStreamAdapter(url, requests.get(zip_url, stream=True))
            return self.cache[zip_url]

def includeme(config):
    config.add_plugin("downloading", DownloadingFromRepositoryURI)


