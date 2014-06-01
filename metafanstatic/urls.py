# -*- coding:utf-8 -*-
import re
github_rx = re.compile(r"git://github\.com/(\S+)(?:\.git)?$")


def get_repository_fullname_from_url(url):
    """ repository_fullname = :owener/:name"""
    m = github_rx.search(url)
    if m:
        return m.group(1)
    return None
