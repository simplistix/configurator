# Copyright (c) 2011-2012 Simplistix Ltd
# See license.txt for license details.

from . import marker
from ._api import API

class Section(object):

    def __init__(self, source=None):
        self._api = API(source)

    def __getitem__(self, name):
        return self._api.get(name)
    
    def __setitem__(self, name, value):
        self._api.set(name,value)

    def get(self, name, default=None):
        return self._api.get(name, default)
    
    def __getattr__(self, name):
        value = self._api.get(name, marker)
        if value is marker:
            raise AttributeError(name)
        return value

    def __setattr__(self, name, value):
        if name == '_api':
            self.__dict__[name] = value
        self._api.set(name, value)
