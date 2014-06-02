# -*- coding:utf-8 -*-
_data = {
    "sample-bootstrap":
    {
        "name": "sample-bootstrap",
        "main": ["dist/util.js", "dist/util.css"],
        "version": "0.0.1",
        "dependencies": [{"mylib": "0.0.1"}]
    },
    "mylib":
    {
        "name": "mylib",
        "main": ["dist/mylib.js"],
        "version": "0.0.1"
    },
}


def _getTarget():
    from genfa.complement import TotalComplement
    return TotalComplement


def _makeOne(*args, **kwargs):
    return _getTarget()(*args, **kwargs)


data = _data.copy()
bower_directory = "/tmp/bower"
word = "sample-bootstrap"
target = _makeOne(bower_directory)

result = target.complement(word, data)


def test_keys():
    assert sorted(list(result.keys())) == ["mylib", "pro", "sample-bootstrap"]


def test_pro():
    assert result["pro"] == ["mylib", "sample-bootstrap"]


def test_package():
    assert result["sample-bootstrap"]["package"] == "meta.js.sample-bootstrap"


def test_pythonname():
    assert result["sample-bootstrap"]["pythonname"] == "sample_bootstrap"


def test_module():
    assert result["sample-bootstrap"]["module"] == "js.sample_bootstrap"


def test_bowerdirectory():
    assert result["sample-bootstrap"]["bower_directory"] == "/tmp/bower"


def test_main_js_path_list():
    assert result["sample-bootstrap"]["main_js_path_list"] == ['/tmp/bower/dist/util.js', '/tmp/bower/dist/util.css']

