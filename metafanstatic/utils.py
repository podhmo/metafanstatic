# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import json


def safe_json_load(filename, retry=False):
    try:
        with open(filename, "r") as io:
            return json.load(io)
    except ValueError:
        if retry:
            raise Exception("json file is broken: %s", filename)
        logger.warn("jsondict is broken in %s. trying removing cache", filename, )
        with open(filename, "wb") as wf:
            json.dump({}, wf)
        return safe_json_load(filename, retry=True)


class reify(object):
    """ copy of pyramid.decorator:reify"""
    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except:  # pragma: no cover
            pass

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val

