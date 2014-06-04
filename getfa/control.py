# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

import re
github_rx = re.compile(r"git://github\.com/(\S+)(?:\.git)?$")


def get_repository_fullname_from_url(url):
    """ repository_fullname = :owener/:name"""
    m = github_rx.search(url)
    if m:
        return m.group(1).replace(".git", "")
    return None


class GithubAPIControl(object):
    def on_versions(self, fullname):  # fullname = :author:/:package:
        if fullname:
            return "https://api.github.com/repos/{name}/tags".format(name=fullname)
        raise NotImplementedError(fullname)

    def on_lookup(self, word=""):
        return "https://bower.herokuapp.com/packages/{}".format(word)

    def on_search(self, word=""):
        return "https://bower.herokuapp.com/packages/search/{}".format(word)

    def on_download(self, fullname, version=None):
        if version is None:
            return "https://github.com/{name}/archive/master.zip".format(name=fullname)
        else:
            return "https://github.com/{name}/archive/{version}.zip".format(name=fullname, version=version)

    def on_tags(self, fullname, version):
        fmt = "https://api.github.com/repos/{name}/git/trees/{sha}"
        return fmt.format(name=fullname, sha=version)

    def on_rawfile(self, fullname, version, filepath):
        fmt = "https://raw.githubusercontent.com/{name}/{version}/{filepath}"
        return fmt.format(name=fullname, version=version, filepath=filepath)

    def fullname_of_url(self, url):
        return get_repository_fullname_from_url(url)
