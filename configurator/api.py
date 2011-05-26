# Copyright (c) 2011 Simplistix Ltd
# See license.txt for license details.

class Attribute:

    def __init__(self,value,source):
        self.value = value
        self.source = source
        
class API(dict):

    # access
    
    def get(self,name,default=None):
        history = dict.get(self,name)
        if history is None:
            return default
        return history[-1].value

    # modification
    
    def set(self,name,value,source=None):
        if name not in self:
            self[name]=[]
        self[name].append(Attribute(value,source))

    def append(self,name,value,source=None):
        raise NotImplementedError()

    def remove(self,name,value,source=None):
        raise NotImplementedError()

    # introspection
    
    def source(self,name):
        return self[name][-1].source

    def history(self,name):
        return self[name]


    
