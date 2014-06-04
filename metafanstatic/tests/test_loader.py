# -*- coding:utf-8 -*-
# -*- coding:utf-8 -*-
from korpokkur.testing import file_structure_from_dict
import os.path
import shutil

here = os.path.dirname(os.path.abspath(__name__))
if os.path.exists(os.path.join(here, "sample")):
    shutil.rmtree(os.path.join(here, "sample"))

bower_json = """{
  "name": "sample",
  "version": "0.0.1",
  "description": "sample-package",
  "main": ["dist/sample.js"]
}
"""

file_structure = {
    "sample": {
        "bower.json": bower_json,
        "dist": {
            "sample.js": "//sample.js"
        }
    }
}


file_structure_from_dict(here, file_structure)


def _getTarget():
    from metafanstatic.loading import Loader
    return Loader


def _makeOne(*args, **kwargs):
    return _getTarget()(*args, **kwargs)

loader = _makeOne()
bowerpath = os.path.join(here, "sample")
result = loader.load(bowerpath)


def test_main():
    assert "main" in result


def test_bower_directory():
    assert "bower_directory" in result
