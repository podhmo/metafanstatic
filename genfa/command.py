# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import json
import argparse
import sys
import os.path
from .loading import Loader, OverrideLoader, CreateConfigMessageExit, out


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


def main(sys_args=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("program")
    sub_parsers = parser.add_subparsers()

    scan_parser = sub_parsers.add_parser("scan")
    scan_parser.add_argument("--logging", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    scan_parser.add_argument("files", nargs="+")
    scan_parser.set_defaults(logging="DEBUG", func=scanning)

    args = parser.parse_args(sys_args)
    try:
        func = args.func
    except AttributeError:
        parser.error("unknown action")
    return func(args)
