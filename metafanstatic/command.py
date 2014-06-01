# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import argparse
import os.path
import sys
from configless import Configurator
from .viewhelpers import namenize

def get_app(setting={
        "entry_points_name": "korpokkur.scaffold",
        "listing.search.url": "https://bower.herokuapp.com/packages/search/",
        "listing.lookup.url": "https://bower.herokuapp.com/packages/",
        "listing.cache.dirpath": "/tmp/metafanstaticcache",
        "listing.cache.versions.filename": "cache.versions.json",
        "listing.cache.url.filename": "cache.url.json",
        "information.cache.dirpath": "/tmp/metafanstaticcache",
        "information.cache.trees.filename": "cache.trees.json",
        "information.cache.bower.filename": "cache.bower.json",
        "download.cache.dirpath": "/tmp/metafanstaticcache",
        "download.cache.filename": "cache.json",
        "extracting.work.dirpath": "/tmp/metafanstaticwork",
        "extracting.cache.filename": "cache.json",
        "creation.work.dirpath": "/tmp/metafanstaticbuild",
        "creation.cache.filename": "cache.json",
        "input.prompt": "{word}?",
}):
    config = Configurator(setting=setting)
    config.include("metafanstatic.listing")
    config.include("metafanstatic.downloading")
    config.include("metafanstatic.extracting")
    config.include("metafanstatic.information")
    return config  # xxx:


def setup_logging(app, args):
    if args.logging is None:
        return
    else:
        import logging
        level = getattr(logging, args.logging)
        logging.basicConfig(level=level)


def listing(args):
    app = get_app()
    setup_logging(app, args)
    for val in app.activate_plugin("listing").iterate_search(args.word):
        print('{val[name]}: {val[url]}'.format(val=val))


def lookup(args):
    app = get_app()
    setup_logging(app, args)
    for val in app.activate_plugin("listing").iterate_lookup(args.word):
        print('{val[name]}: {val[url]}'.format(val=val))


def versions(args):
    app = get_app()
    setup_logging(app, args)
    if args.describe == "json":
        for val in app.activate_plugin("listing").iterate_versions(args.word):
            print(val)
    elif args.describe == "version":
        for val in app.activate_plugin("listing").iterate_versions(args.word):
            print(val["name"])
    elif args.describe == "zip":
        for val in app.activate_plugin("listing").iterate_versions(args.word):
            print(val["zipball_url"])


def get_url_from_word(app, word):
    if "::/" in word:
        return word
    for val in app.activate_plugin("listing").iterate_lookup(word):
        return val["url"]


def get_url_and_version(app, word, version, restriction=""):
    url = get_url_from_word(app, word)
    if version is not None:
        return url, version
    logger.info("version is not specified. finding latest version of %s", word)
    versions = app.activate_plugin("listing").iterate_versions(word, url=url)

    if not versions:
        sys.exit(0)  # xxx:
    versions = [v["name"] for v in versions]
    version = choose_it(versions, restriction)
    logger.info("latest version is %s", version)
    return url, version


def err(line):
    sys.stderr.write(line)
    sys.stderr.write("\n")
    sys.stderr.flush()


def choose_it(xs, restriction=""):
    from semver import max_satisfying
    return max_satisfying(xs, restriction, loose=True)


def choose_it_by_hand(xs):
    for i, line in enumerate(xs[:10]):
        err("{}: {}".format(i, line))

    while True:
        try:
            err("please, choose item")
            n = sys.stdin.readline().strip()
            return xs[int(n)]
        except (TypeError, IndexError, ValueError) as e:
            logger.warn(e)


def downloading(args):
    app = get_app()
    setup_logging(app, args)
    url, version = get_url_and_version(app, args.word, args.version, args.restriction or "")
    print(app.activate_plugin("downloading").download(url, version))


def extracting(args):
    app = get_app()
    setup_logging(app, args)
    url, version = get_url_and_version(app, args.word, args.version, args.restriction or "")
    zipppath = app.activate_plugin("downloading").download(url, version)
    print(app.activate_plugin("extracting").extract(args.word, version, zipppath))


class DependencyInformation(object):
    def __init__(self, app, local=False):
        self.app = app
        self.result = {}
        self.history = {}
        self.local = local

    def write(self, word, info, version):
        self.result[word] = {"restriction": info.version,
                             "name": word,
                             "pythonname": namenize(word),
                             "description": info.description,
                             "bower_dir_path": info.bower_dir_path,
                             "info": info,
                             "package": info.package,
                             "main_js_path_list": info.main_js_path_list,
                             "version": version}
        if info.dependencies:
            self.result[word]["dependencies"] = [d["name"] for d in info.dependencies]

    def _collect(self, word, version, raw_expression=""):
        if word in self.history:
            return
        self.history[word] = 1
        url, version = get_url_and_version(self.app, word, version, raw_expression)

        if self.local:
            zipppath = self.app.activate_plugin("downloading").download(url, version)
            bower_json_path = (self.app.activate_plugin("extracting").extract(word, version, zipppath))
            info = self.app.activate_plugin("information", bower_json_path, version)
        else:
            info = self.app.activate_plugin("information:remote", url, version)
        self.write(word, info, version)
        for data in info.dependencies:
            self._collect(data["name"], None, data["version"])

    def collect(self, word, version, raw_expression=""):
        self._collect(word, version, version)
        # pro
        queue = [word]
        pro = []
        while queue:
            word = queue.pop(0)
            if word not in pro:
                pro.append(word)
            if "dependencies" in self.result[word]:
                queue.extend(self.result[word]["dependencies"])
        self.result["pro"] = list(reversed(pro))

        # dependencies_module
        for name in self.result["pro"]:
            subinfo = self.result[name]
            subinfo["dependencies_module"] = modules = []
            for parent_name in subinfo.get("dependencies", []):
                modules.append(self.result[parent_name]["info"].module)
        return self.result


def information(args):
    app = get_app()
    setup_logging(app, args)
    _, version = get_url_and_version(app, args.word, args.version, args.restriction or "")
    dinfo = DependencyInformation(app, args.local)
    result = dinfo.collect(args.word, version, version)
    import pprint
    pprint.pprint(result)


def creation(args):
    app = get_app()
    setup_logging(app, args)
    url, version = get_url_and_version(app, args.word, args.version, args.restriction or "")

    # korpokkur
    app.include("korpokkur.scaffoldgetter")
    app.include("korpokkur.walker")
    app.include("korpokkur.detector")
    app.include("korpokkur.input")
    app.include("korpokkur.reproduction")
    app.include("korpokkur.emitter.mako")

    getter = app.activate_plugin("scaffoldgetter")
    scaffold = getter.get_scaffold("metafanstatic")
    deps_result = DependencyInformation(app, True).collect(args.word, version, version)
    for name in deps_result["pro"]:
        paramaters = {}
        paramaters.update(deps_result[name])
        input = app.activate_plugin("input.cli", scaffold)
        input.update(paramaters)
        emitter = app.activate_plugin("emitter.mako")
        reproduction = app.activate_plugin("reproduction.physical", emitter, input)
        detector = app.activate_plugin("detector")
        walker = app.activate_plugin("walker", input, detector, reproduction)
        dst = app.registry.setting["creation.work.dirpath"]
        input.update({"Undefined": "`Undefined"})
        scaffold.walk(walker, dst, overwrite=True)
        print(os.path.join(dst, paramaters["package"]))


def main(sys_args=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("program")
    sub_parsers = parser.add_subparsers()

    list_parser = sub_parsers.add_parser("list")
    list_parser.add_argument("--logging", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    list_parser.add_argument("--clear", action="store_true", default=False)
    list_parser.add_argument("word")
    list_parser.set_defaults(logging="DEBUG", func=listing)

    lookup_parser = sub_parsers.add_parser("lookup")
    lookup_parser.add_argument("--clear", action="store_true", default=False)
    lookup_parser.add_argument("--logging", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    lookup_parser.add_argument("word")
    lookup_parser.set_defaults(logging="DEBUG", func=lookup)

    versions_parser = sub_parsers.add_parser("versions")
    versions_parser.add_argument("--clear", action="store_true", default=False)
    versions_parser.add_argument("--logging", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    versions_parser.add_argument("--describe", choices=["version", "zip", "json"])
    versions_parser.add_argument("word")
    versions_parser.set_defaults(logging="DEBUG", func=versions, describe="version")

    download_parser = sub_parsers.add_parser("download")
    download_parser.add_argument("--clear", action="store_true", default=False)
    download_parser.add_argument("--logging", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    download_parser.add_argument("--version")
    download_parser.add_argument("--restriction")
    download_parser.add_argument("word")
    download_parser.set_defaults(logging="DEBUG", func=downloading, version=None)

    extract_parser = sub_parsers.add_parser("extract")
    extract_parser.add_argument("--clear", action="store_true", default=False)
    extract_parser.add_argument("--logging", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    extract_parser.add_argument("--version")
    extract_parser.add_argument("--restriction")
    extract_parser.add_argument("word")
    extract_parser.set_defaults(logging="DEBUG", func=extracting)

    information_parser = sub_parsers.add_parser("information")
    information_parser.add_argument("--logging", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    information_parser.add_argument("--version")
    information_parser.add_argument("--restriction")
    information_parser.add_argument("--local", action="store_true", default=False)
    information_parser.add_argument("word")
    information_parser.add_argument("--description", action="store_true")
    information_parser.set_defaults(logging="INFO", func=information)

    create_parser = sub_parsers.add_parser("create")
    create_parser.add_argument("--logging", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    create_parser.add_argument("--restriction")
    create_parser.add_argument("--version")
    create_parser.add_argument("word")
    create_parser.set_defaults(logging="DEBUG", func=creation)

    args = parser.parse_args(sys_args)
    try:
        func = args.func
    except AttributeError:
        parser.error("unknown action")
    return func(args)
