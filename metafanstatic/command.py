# -*- coding:utf-8 -*-
import argparse
import sys
from configless import Configurator
import os.path
import json
from .information import GithubInformation
from .downloading import GithubDownloading, RawDownloading, NotZipFile
from .detector import GithubDetector
from .classifier import GithubClassifier
from .dependency import GithubDependencyCollector
from .loading import Loader, OverrideLoader, CreateConfigMessageExit, out
from .complement import TotalComplement
from .generating import Generating

import logging
logger = logging.getLogger(__name__)
from semver import logger as semver_logger
semver_logger.propagate = False
from requests.packages.urllib3.connectionpool import log as requests_logger
requests_logger.propagate = False
logging.basicConfig(level=logging.DEBUG)


def scanning(args):
    loader = Loader()
    override = OverrideLoader()
    create_config = CreateConfigMessageExit()
    loaders = [override, loader, create_config]
    result = {}

    def load(f):
        for loader in loaders:
            data = loader.load(f, noexception=True)
            if data is not None:
                return data

    for f in args.files:
        params = load(f)
        name = params["name"]
        result[name] = params
    out(json.dumps(result, indent=2, ensure_ascii=False))


def creation(args):
    with open(args.config) as rf:
        params = json.load(rf)

    complement = TotalComplement()
    complement.complement(params)
    config = Configurator({
        "entry_points_name": "korpokkur.scaffold",
        "input.prompt": "{word}?"
    })

    generating = Generating(config)
    for c in params["total"]["pro"]:
        generating.generate(params[c], args.dst)


def get_app(args):
    config = Configurator({"cachedir": args.cachedir})
    config.include("metafanstatic.information")
    config.include("metafanstatic.downloading")
    return config


def versions(args):
    app = get_app(args)
    information = GithubInformation(app)
    for val in information.version(args.word):
        print(val["name"])


def searching(args):
    app = get_app(args)
    information = GithubInformation(app)
    for val in information.search(args.word):
        print("{val[name]} {val[url]}".format(val=val))


def downloading(args):
    if args.config:
        return downloading_from_config(args)
    if args.url:
        return downloading_from_url(args)
    app = get_app(args)
    information = GithubInformation(app)
    downloading = GithubDownloading(app, information)
    try:
        print(downloading.download(args.word, args.dst, args.version))
    except NotZipFile:
        detector = GithubDetector(app)
        correct_version = detector.choose_version(information, args.word, args.version)
        print(downloading.download(args.word, args.dst, correct_version))


def downloading_from_url(args):
    app = get_app(args)
    downloading = RawDownloading(app)
    print(downloading.download(args.url, args.dst))


def downloading_from_config(args):
    app = get_app(args)
    information = GithubInformation(app)
    github_downloading = GithubDownloading(app, information)
    raw_downloading = RawDownloading(app)

    with open(args.config, "r") as rf:
        params = json.load(rf)

    detector = GithubDetector(app)

    for name, data in params.items():
        if "rawurl" in data:
            print(raw_downloading.download(data["rawurl"], args.dst, name=data["name"]))
        else:
            try:
                print(github_downloading.download(data["name"], args.dst, data["version"]))
            except NotZipFile:
                correct_version = detector.choose_version(information, data["name"], data["version"])
                print(github_downloading.download(data["name"], args.dst, correct_version))


def dependency(args):
    app = get_app(args)
    information = GithubInformation(app)
    detector = GithubDetector(app)
    classifier = GithubClassifier(app)
    dependency = GithubDependencyCollector(app, information, detector, classifier)

    if not args.recursive:
        result = dependency.one_dependency(args.word, args.version)
    else:
        result = dependency.recursive_dependency(args.word, args.version)
    print(json.dumps(result, indent=2, ensure_ascii=False))


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


def listing(args):
    def import_symbol(symbol):
        return pkg_resources.EntryPoint.parse("x=%s" % symbol).load(False)

    import pkg_resources
    from fanstatic import Resource
    for d in pkg_resources.working_set:
        for v, val in d.get_entry_map('fanstatic.libraries').items():
            module_name = val.module_name
            m = import_symbol(module_name)
            for name, ob in m.__dict__.items():
                if isinstance(ob, Resource):
                    print("from {module} import {name}; {name}.need()".format(module=val.module_name, name=name))


def main(sys_args=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--logging", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    parser.add_argument("--cachedir", default="/tmp/fanstatic")
    parser.add_argument("program")
    sub_parsers = parser.add_subparsers()

    #  genfa

    scan_parser = sub_parsers.add_parser("scan")
    scan_parser.add_argument("files", nargs="+")
    scan_parser.set_defaults(logging="DEBUG", func=scanning)

    create_parser = sub_parsers.add_parser("create")
    create_parser.add_argument("config")
    create_parser.add_argument("dst")
    create_parser.set_defaults(logging="DEBUG", func=creation)

    list_parser = sub_parsers.add_parser("list")
    list_parser.set_defaults(logging="DEBUG", func=listing)

    # getfa

    version_parser = sub_parsers.add_parser("version")
    version_parser.add_argument("word")
    version_parser.set_defaults(logging="DEBUG", func=versions)

    search_parser = sub_parsers.add_parser("search")
    search_parser.add_argument("word")
    search_parser.set_defaults(logging="DEBUG", func=searching)

    clear_parser = sub_parsers.add_parser("clear")
    clear_parser.add_argument("word", nargs="?")
    clear_parser.set_defaults(logging="DEBUG", func=clear)

    dependency_parser = sub_parsers.add_parser("dependency")
    dependency_parser.add_argument("word")
    dependency_parser.add_argument("--local", action="store_true", default=False)
    dependency_parser.add_argument("--recursive", "-r", action="store_true", default=False)
    dependency_parser.add_argument("--version", "-v", default="")
    dependency_parser.set_defaults(logging="DEBUG", func=dependency)

    download_parser = sub_parsers.add_parser("download")
    download_parser.add_argument("--version", default=None)
    download_parser.add_argument("--config", default=None)
    download_parser.add_argument("--url", default=None)
    download_parser.add_argument("word", default=None, nargs="?")
    download_parser.add_argument("dst", default=".", nargs="?")
    download_parser.set_defaults(logging="DEBUG", func=downloading)

    args = parser.parse_args(sys_args)
    try:
        func = args.func
    except AttributeError:
        parser.error("unknown action")
    return func(args)

