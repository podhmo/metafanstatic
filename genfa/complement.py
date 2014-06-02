# -*- coding:utf-8 -*-
from .viewhelpers import namenize
import os.path


class TotalComplement(object):
    def __init__(self, dirpath):
        self.unit_complement = UnitComplement(self)
        self.bower_directory = dirpath

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
        data["pro"] = self.complement_pro(data, word)
        for name in data["pro"]:
            self.unit_complement.complement(name, data[name])
        return data


class UnitComplement(object):
    """
    package = meta.js.foo-bar
    module = js.foo_bar
    pythonname = js.foo_bar
    """
    def __init__(self, total):
        self.total = total

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
        return "js.{}".format(namenize(name))

    def complement_package_name(self, name):
        return "meta.js.{}".format(name)

    def complement_path_list(self, data):
        main = data["main"]
        if isinstance(main, (list, tuple)):
            main_files = main
        else:
            main_files = [main]
        return [os.path.join(self.bower_directory, f) for f in main_files]
