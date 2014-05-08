# -*- coding:utf-8 -*-
from configless.interfaces import IPlugin
from .interfaces import IDownloading
from zope.interface import implementer
import re
import requests
import os.path

from .cache import JSONFileCache

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
            return self.cache.store_stream(zip_url, _FileStreamAdapter(url, requests.get(zip_url, stream=True)))

def includeme(config):
    config.add_plugin("downloading", DownloadingFromRepositoryURI)


