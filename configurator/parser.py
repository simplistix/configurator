# Copyright (c) 2011 Simplistix Ltd
# See license.txt for license details.

class Parser(object):

    def __init__(self):
        raise NotImplementedError()

    def set_format(self, extension, parser):
        raise NotImplementedError()
        
    def set_schema(self, schema):
        raise NotImplementedError()
        
    def parse(self, config):
        raise NotImplementedError()
        
