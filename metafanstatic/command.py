# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import argparse
import sys
from configless import Configurator

def get_app(setting={"listing.search.url": "https://bower.herokuapp.com/packages/search/"}):
    config = Configurator(setting=setting)
    config.include("metafanstatic.listing")
    return config #xxx:

def listing(args):
    app = get_app()
    for val in app.activate_plugin("listing").iterate_repository(args.word):
        print('{val[name]}: {val[url]}'.format(val=val))


def main(sys_args=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("program")
    sub_parsers = parser.add_subparsers()

    list_parser = sub_parsers.add_parser("list")
    list_parser.add_argument("--logging", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    list_parser.add_argument("word")
    list_parser.set_defaults(func=listing)

    args = parser.parse_args(sys_args)
    try:
        func = args.func
    except AttributeError:
        parser.error("unknown action")
    return func(args)

