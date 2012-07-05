# Copyright (c) 2011-2012 Simplistix Ltd
# See license.txt for license details.

# a marker for defaults and missing values
class Marker(object):
    def __repr__(self):
        return '<Marker>'
marker = Marker()

_parsers = {}
_configs = {}

def parse(source, parser=None, format=None, schema=None, transform=None, process=True):
    "Parse a configuration"
    # source can be:
    # - a file path
    # - a url
    # - an object with a read method (must supply parser)
    # schema can be:
    # - a parsed schema
    # - a file path
    if format is not None:
        parser = _parsers[format]
    
    if isinstance(source, basestring):
        stream = open(source)
    else:
        stream = source
        source = None
        
    config = parser(source, source)
    a = api(config)
    if schema is not None:
        if isinstance(schema, basestring):
            schema = parse(schema)
        a.apply_schema(schema)
    raise NotImplementedError()

def api(section):
    "Get the Configurator API for a particular section"
    return section._api

def process(section):
    "Process any actions present on the section passed"
    raise NotImplementedError()

def transform(section, *transformations):
    "Apply the supplied transformations to the section specified."
    raise NotImplementedError()

def set_configuration(config, name=None):
    "Store a configuration for later retrieval"
    raise NotImplementedError()
    _configs[name] = config

def get_configuration(name=None):
    "Retrieve a previously stored configuration"
    raise NotImplementedError()
    return _configs[name]

def register_parser(extension, parser):
    "Register a parser for use with files of a particular extension"
    raise NotImplementedError
    _parsers[extension] = parser
    # strip off leading dot if there :-)
