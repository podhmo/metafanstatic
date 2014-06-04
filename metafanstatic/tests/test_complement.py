# -*- coding:utf-8 -*-
_data = {
    "sample-bootstrap":
    {
        "name": "sample-bootstrap",
        "bower_directory": "/tmp/bower/sample-bootstrap",
        "main": ["dist/util.js", "dist/util.css"],
        "version": "0.0.1",
        "dependencies": {"mylib": "0.0.1"}
    },
    "mylib":
    {
        "name": "mylib",
        "bower_directory": "/tmp/bower/mylib",
        "main": ["dist/mylib.js"],
        "version": "0.0.1"
    },
}


def _getTarget():
    from metafanstatic.complement import TotalComplement
    return TotalComplement


def _makeOne(*args, **kwargs):
    return _getTarget()(*args, **kwargs)


def dummy_mylib_is_installed_generator(decider):
    yield "meta.js.mylib"


data = _data.copy()
target = _makeOne(package_name_generator=dummy_mylib_is_installed_generator)

result = target.complement(data)


def test_keys():
    assert sorted(list(result.keys())) == ["mylib", "sample-bootstrap", "total"]


def test_total_pro():
    assert result["total"]["pro"] == ["mylib", "sample-bootstrap"]


def test_total_installed():
    assert result["total"]["installed"] == ["meta.js.mylib"]


def test_total_notistalled():
    assert result["total"]["notinstalled"] == ["meta.js.sample-bootstrap"]


def test_package():
    assert result["sample-bootstrap"]["package"] == "meta.js.sample-bootstrap"


def test_pythonname():
    assert result["sample-bootstrap"]["pythonname"] == "sample_bootstrap"


def test_module():
    assert result["sample-bootstrap"]["module"] == "js.sample_bootstrap"


def test_bowerdirectory():
    assert result["sample-bootstrap"]["bower_directory"] == "/tmp/bower/sample-bootstrap"


def test_main_js_path_list():
    assert result["sample-bootstrap"]["main_js_path_list"] == ['/tmp/bower/sample-bootstrap/dist/util.js', '/tmp/bower/sample-bootstrap/dist/util.css']

