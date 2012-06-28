# Copyright (c) 2011 Simplistix Ltd
# See license.txt for license details.

# a marker for defaults and missing values
class Marker(object):
    def __repr__(self):
        return '<Marker>'
marker = Marker()

def parse(config, schema=None):
    raise NotImplementedError()

def api(section):
    "Get the Configurator API for a particular section"
    return section._api

def process(section):
    "Process any actions present on the section passed"
    raise NotImplementedError()

class Parser(object):

    def __init__(self):
        raise NotImplementedError()

    def set_format(self, extension, parser):
        raise NotImplementedError()
        
    def set_schema(self, schema):
        raise NotImplementedError()
        
    def parse(self, config):
        raise NotImplementedError()
        
