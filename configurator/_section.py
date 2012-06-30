# Copyright (c) 2011-2012 Simplistix Ltd
# See license.txt for license details.

from . import marker
from ._api import API
from ._utils import get_source

class Section(object):
    def __init__(self, source=None):
        self._api = API(source or get_source())

    def __getitem__(self, name):
        value =  self._api.get(name, marker)
        if value is marker:
            raise KeyError(name)
        return value
    
    def __setitem__(self, name, value):
        self._api.set(name, value, source=get_source())

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
        else:
            self._api.set(name, value, get_source())

    def keys(self):
        for a in self._api.items():
            if a.name:
                yield a.name

    def values(self):
        for a in self._api.items():
            yield a.value

    def items(self):
        for a in self._api.items():
            yield a.name, a.value

    def __iter__(self):
        return self.keys()
