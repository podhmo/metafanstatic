# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import argparse
import os.path
import sys
from configless import Configurator

def get_app(setting={
        "entry_points_name": "korpokkur.scaffold", 
        "listing.search.url": "https://bower.herokuapp.com/packages/search/", 
        "listing.lookup.url": "https://bower.herokuapp.com/packages/", 
        "download.cache.dirpath" : "/tmp/metafanstaticcache",
        "download.cache.filename" : "cache.json", 
        "extracting.work.dirpath": "/tmp/metafanstaticwork", 
        "extracting.cache.filename" : "cache.json", 
        "creation.work.dirpath": "/tmp/metafanstaticbuild", 
        "creation.cache.filename" : "cache.json", 
}):
    config = Configurator(setting=setting)
    config.include("metafanstatic.listing")
    config.include("metafanstatic.downloading")
    config.include("metafanstatic.extracting")
    config.include("metafanstatic.information")
    return config #xxx:

def listing(args):
    app = get_app()
    for val in app.activate_plugin("listing").iterate_search(args.word):
        print('{val[name]}: {val[url]}'.format(val=val))

def lookup(args):
    app = get_app()
    for val in app.activate_plugin("listing").iterate_lookup(args.word):
        print('{val[name]}: {val[url]}'.format(val=val))

def downloading(args):
    app = get_app()
    print(app.activate_plugin("downloading").download(args.url))

def extracting(args):
    app = get_app()
    zipppath = app.activate_plugin("downloading").download(args.url)
    print(app.activate_plugin("extracting").extract(zipppath))

def information(args):
    app = get_app()
    zipppath = app.activate_plugin("downloading").download(args.url)
    bower_json_path = (app.activate_plugin("extracting").extract(zipppath))
    information = app.activate_plugin("information", bower_json_path)
    print(information.description)
    print(information.dependencies)
    print(information.exists_info())

def creation(args):
    app = get_app()
    zipppath = app.activate_plugin("downloading").download(args.url)
    bower_json_path = (app.activate_plugin("extracting").extract(zipppath))
    information = app.activate_plugin("information", bower_json_path)

    ## korpokkur
    app.include("korpokkur.scaffoldgetter")
    app.include("korpokkur.walker")
    app.include("korpokkur.detector")
    app.include("korpokkur.input")
    app.include("korpokkur.reproduction")
    app.include("korpokkur.emitter.mako")

    getter = app.activate_plugin("scaffoldgetter")
    scaffold = getter.get_scaffold("metafanstatic")
    input = app.activate_plugin("input.dict", scaffold, information.data)
    information.push_data(input)
    emitter = app.activate_plugin("emitter.mako")
    reproduction = app.activate_plugin("reproduction.physical", emitter, input)
    detector = app.activate_plugin("detector")
    walker = app.activate_plugin("walker", input, detector, reproduction)
    dst = app.registry.setting["creation.work.dirpath"]
    input.update({"Undefined":"`Undefined"})
    scaffold.walk(walker, dst, overwrite=True)
    print(os.path.join(dst, information.package))

def main(sys_args=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("program")
    sub_parsers = parser.add_subparsers()

    list_parser = sub_parsers.add_parser("list")
    list_parser.add_argument("--logging", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    list_parser.add_argument("word")
    list_parser.set_defaults(func=listing)

    lookup_parser = sub_parsers.add_parser("lookup")
    lookup_parser.add_argument("--logging", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    lookup_parser.add_argument("word")
    lookup_parser.set_defaults(func=lookup)

    download_parser = sub_parsers.add_parser("download")
    download_parser.add_argument("--logging", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    download_parser.add_argument("url")
    download_parser.set_defaults(func=downloading)

    extract_parser = sub_parsers.add_parser("extract")
    extract_parser.add_argument("--logging", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    extract_parser.add_argument("url")
    extract_parser.set_defaults(func=extracting)

    information_parser = sub_parsers.add_parser("information")
    information_parser.add_argument("--logging", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    information_parser.add_argument("url")
    information_parser.add_argument("--description", action="store_true")
    information_parser.set_defaults(func=information)

    create_parser = sub_parsers.add_parser("create")
    create_parser.add_argument("--logging", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    create_parser.add_argument("url")
    create_parser.set_defaults(func=creation)

    args = parser.parse_args(sys_args)
    try:
        func = args.func
    except AttributeError:
        parser.error("unknown action")
    return func(args)

