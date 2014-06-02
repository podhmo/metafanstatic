# -*- coding:utf-8 -*-
from .viewhelpers import namenize
import os.path
import pkg_resources
from .decorator import reify


class NameRoleDecider(object):
    def __init__(self):
        self.package_prefix = "meta.js"
        self.module_prefix = "js"

    def is_needed_package(self, name):
        return name.startswith(self.package_prefix)

    def is_needed_module(self, name):
        return name.startswith(self.module_prefix)

    def as_package_name(self, name):
        return "{}.{}".format(self.package_prefix, name)

    def as_module_name(self, name):
        return "{}.{}".format(self.module_prefix, namenize(name))


class PackageNameGenerator(object):
    def __init__(self, decider):
        self.decider = decider

    def __iter__(self):
        for dist in pkg_resources.working_set:
            name = dist.project_name
            if self.decider.is_needed_package(name):
                yield name


class PackageNameDivider(object):
    def __init__(self, packages, generator):
        self.packages = packages
        self.generator = generator

    @reify
    def divided(self):
        installed = []
        notinstalled = []
        all_installed = set(self.generator)

        for name in self.packages:
            if name in all_installed:
                installed.append(name)
            else:
                notinstalled.append(name)
        return (installed, notinstalled)

    @property
    def installed(self):
        return self.divided[0]

    @property
    def notinstalled(self):
        return self.divided[1]


class TotalComplement(object):
    def __init__(self, dirpath, package_name_generator):
        self.decider = NameRoleDecider()
        self.unit_complement = UnitComplement(self, self.decider)
        self.bower_directory = dirpath
        self.package_name_generator = package_name_generator(self.decider)

    def complement_pro(self, data, word):
        queue = [word]
        pro = []
        while queue:
            word = queue.pop(0)
            if word not in pro:
                pro.append(word)
            if "dependencies" in data[word]:
                for data in data[word].get("dependencies", []):
                    queue.append(list(data.keys())[0])
        return list(reversed(pro))

    def complement(self, word, data):
        data["total"] = info = {}
        info["pro"] = self.complement_pro(data, word)
        for name in info["pro"]:
            self.unit_complement.complement(name, data[name])

        packages = [data[name]["package"] for name in info["pro"]]
        divider = PackageNameDivider(packages, self.package_name_generator)
        info["installed"] = divider.installed
        info["notinstalled"] = divider.notinstalled
        return data


class UnitComplement(object):
    """
    package = meta.js.foo-bar
    module = js.foo_bar
    pythonname = js.foo_bar
    """
    def __init__(self, total, decider):
        self.total = total
        self.decider = decider

    @property
    def bower_directory(self):
        return self.total.bower_directory

    def complement(self, name, data):
        data["pythonname"] = self.complement_python_name(name)
        data["module"] = self.complement_module_name(name)
        data["package"] = self.complement_package_name(name)
        data["main_js_path_list"] = self.complement_path_list(data)
        data["bower_directory"] = self.bower_directory
        return data

    def complement_python_name(self, name):
        return namenize(name)

    def complement_module_name(self, name):
        return self.decider.as_module_name(name)

    def complement_package_name(self, name):
        return self.decider.as_package_name(name)

    def complement_path_list(self, data):
        main = data["main"]
        if isinstance(main, (list, tuple)):
            main_files = main
        else:
            main_files = [main]
        return [os.path.join(self.bower_directory, f) for f in main_files]
