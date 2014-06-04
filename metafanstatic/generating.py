# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from .decorator import reify


def includeme(config):
    config.include("korpokkur.scaffoldgetter")
    config.include("korpokkur.walker")
    config.include("korpokkur.detector")
    config.include("korpokkur.input")
    config.include("korpokkur.reproduction")
    config.include("korpokkur.emitter.mako")


def get_input(config, scaffold):
    return config.activate_plugin("input.cli", scaffold)


def get_walker(config, input):
    emitter = config.activate_plugin("emitter.mako")
    reproduction = config.activate_plugin("reproduction.physical", emitter, input)
    detector = config.activate_plugin("detector")
    return config.activate_plugin("walker", input, detector, reproduction)


def get_scaffold(config):
    getter = config.activate_plugin("scaffoldgetter")
    scaffold = getter.get_scaffold("metafanstatic")
    return scaffold


class Generating(object):
    def __init__(self, config):
        self.config = config
        self.config.include("metafanstatic.generating")

    @reify
    def input(self):
        return get_input(self.config, self.scaffold)

    @reify
    def scaffold(self):
        return get_scaffold(self.config)

    @reify
    def walker(self):
        return get_walker(self.config, self.input)

    def generate(self, paramater, dst):
        self.input.clear()
        self.input.update(paramater)
        self.scaffold.walk(self.walker, dst, overwrite=True)
