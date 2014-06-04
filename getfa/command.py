# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
import argparse
import sys
from .information import GithubInformation
from .downloading import GithubDownloading
from configless import Configurator


def get_app(args):
    config = Configurator({"cachedir": args.cachedir})
    config.include("getfa.information")
    config.include("getfa.downloading")
    return config


def versions(args):
    app = get_app(args)
    information = GithubInformation(app)
    for val in information.version(args.word):
        # print(val["zipball_url"])
        print(val["name"])

def searching(args):
    app = get_app(args)
    information = GithubInformation(app)
    for val in information.search(args.word):
        print(val)


def downloading(args):
    app = get_app(args)
    information = GithubInformation(app)
    downloading = GithubDownloading(app, information)
    print(downloading.download(args.word, args.version, args.dst))


def clear(args):
    app = get_app(args)
    from .information import ICachedRequesting
    list_of_requesting = app.registry.utilities.lookupAll((), ICachedRequesting)
    if args.word:
        for name, requesting in list_of_requesting:
            requesting.clear(args.word)
    else:
        for name, requesting in list_of_requesting:
            requesting.clear_all()


def main(sys_args=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--logging", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    parser.add_argument("--cachedir", default="/tmp/fanstatic")
    parser.add_argument("program")
    sub_parsers = parser.add_subparsers()

    version_parser = sub_parsers.add_parser("version")
    version_parser.add_argument("word")
    version_parser.set_defaults(logging="DEBUG", func=versions)

    search_parser = sub_parsers.add_parser("search")
    search_parser.add_argument("word")
    search_parser.set_defaults(logging="DEBUG", func=searching)

    clear_parser = sub_parsers.add_parser("clear")
    clear_parser.add_argument("word", nargs="?")
    clear_parser.set_defaults(logging="DEBUG", func=clear)

    download_parser = sub_parsers.add_parser("download")
    download_parser.add_argument("--version", default=None)
    download_parser.add_argument("word")
    download_parser.add_argument("dst", default=".", nargs="?")
    download_parser.set_defaults(logging="DEBUG", func=downloading)

    args = parser.parse_args(sys_args)
    try:
        func = args.func
    except AttributeError:
        parser.error("unknown action")
    return func(args)

