# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
import json
import argparse
import sys
import os.path
from configless import Configurator
from .loading import Loader, OverrideLoader, CreateConfigMessageExit, out
from .complement import TotalComplement
from .generating import Generating


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
        name = os.path.basename(f)
        result[name] = load(f)
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


def main(sys_args=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("program")
    sub_parsers = parser.add_subparsers()

    scan_parser = sub_parsers.add_parser("scan")
    scan_parser.add_argument("--logging", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    scan_parser.add_argument("files", nargs="+")
    scan_parser.set_defaults(logging="DEBUG", func=scanning)

    create_parser = sub_parsers.add_parser("create")
    create_parser.add_argument("--logging", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    create_parser.add_argument("config")
    create_parser.add_argument("dst")
    create_parser.set_defaults(logging="DEBUG", func=creation)

    args = parser.parse_args(sys_args)
    try:
        func = args.func
    except AttributeError:
        parser.error("unknown action")
    return func(args)
