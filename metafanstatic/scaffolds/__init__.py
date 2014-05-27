# -*- coding:utf-8 -*-

from zope.interface import implementer
from korpokkur.interfaces import IScaffoldTemplate
import os.path

# see: korpokkur.interfaces:IScaffoldTemplate


@implementer(IScaffoldTemplate)
class Package(object):

    """fanstatic template for metafanstatic"""
    source_directory = os.path.join(os.path.abspath(os.path.dirname(__file__)), "+package+")
    # varname -> description, default
    expected_words = {
        "package": ("package name", "sample"),
        "description": ("package description", "-"),
        "version": ("version number for project", "0.0")
    }
    __dro__ = ["korpokkur.scaffolds.pygitignore:Package"]  # todo:validation
    template_engine = "mako"

"""
memo:

- version
"""
