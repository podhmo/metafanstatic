# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import sys
import os.path
import json


class TargetNotFound(Exception):
    pass


def find_target_from_candidates(root, targets):
    for r, ds, fs in os.walk(root):
        for f in fs:
            for target in targets:
                if f == target:
                    return os.path.join(r, f)
    raise TargetNotFound("bower.json")


def load_from_file(filename):
    with open(filename, "r") as rf:
        return json.load(rf)


def pack_from_jsondict(jsondict, path):
    result = {}
    result["bower_directory"] = path
    result["name"] = jsondict["name"]
    result["version"] = jsondict.get("version")
    result["dependencies"] = jsondict.get("dependencies", [])
    result["main"] = jsondict["main"]
    return result


class OverrideLoader(object):
    def __init__(self,
                 target_suffix="bower.json",
                 loader=load_from_file,
                 packer=pack_from_jsondict,
                 ):
        self.loader = loader
        self.packer = packer
        self.target_suffix = target_suffix

    def load(self, root, noexception=True):
        filepath = "./{}.{}".format(os.path.basename(root), self.target_suffix)
        if not os.path.exists(filepath):
            return None
        data = self.loader(filepath)
        return self.packer(data, data["bower_directory"])


class Loader(object):
    def __init__(self,
                 finder=find_target_from_candidates,
                 loader=load_from_file,
                 packer=pack_from_jsondict,
                 targets=["bower.json", "complement.json"]):
        self.finder = finder
        self.loader = loader
        self.targets = targets
        self.packer = pack_from_jsondict

    def find_target(self, root):
        return self.finder(root, self.targets)

    def load_from_target(self, path):
        logger.info("loading: %s", path)
        return self.loader(path)

    def load(self, root, noexception=False):
        try:
            path = self.find_target(root)
            data = self.load_from_target(path)
        except TargetNotFound:
            if noexception:
                return None
            raise
        return self.packer(data, os.path.dirname(path))


def err(message):
    sys.stderr.write(message)
    sys.stderr.write("\n")
    sys.stderr.flush()


def out(message):
    sys.stdout.write(message)
    sys.stdout.write("\n")
    sys.stdout.flush()


class CreateConfigMessageExit(object):
    def load(self, f, noexception=True):
        name = os.path.basename(f)
        err("please create config file such as below filename:./{}.bower.json".format(name))
        params = {
            "bower_directory": f,
            "name": name,
            "version": "",
            "description": "",
            "main": ["{}.js".format(name)],
            "dependencies": []
        }
        out(json.dumps(params, indent=2, ensure_ascii=False))
        sys.exit(-1)
