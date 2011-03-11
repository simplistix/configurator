# Copyright (c) 2011 Simplistix Ltd
# See license.txt for license details.

class Attribute:

    def __init__(self,value,source):
        self.value = value
        self.source = source
        
class SectionAPI(dict):

    def get(self,name,default=None):
        history = dict.get(self,name)
        if history is None:
            return default
        return history[-1].value
    
    def set(self,name,value,source=None):
        if name not in self:
            self[name]=[]
        self[name].append(Attribute(value,source))

    def source(self,name):
        return self[name][-1].source

    def history(self,name):
        return self[name]

_marker = object()

class Section(object):

    def __init__(self):
        self._api = SectionAPI()

    def __getitem__(self,name):
        return self._api.get(name)
    
    def __setitem__(self,name,value):
        self._api.set(name,value)

    def get(self,name,default=None):
        return self._api.get(name,default)
    
    def __getattr__(self,name):
        value = self._api.get(name,_marker)
        if value is _marker:
            raise AttributeError(name)
        return value

    def __setattr__(self,name,value):
        if name=='_api':
            self.__dict__[name]=value
        self._api.set(name,value)
