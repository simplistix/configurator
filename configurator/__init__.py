# Copyright (c) 2011-2012 Simplistix Ltd
# See license.txt for license details.

# a marker for defaults and missing values
class Marker(object):
    def __repr__(self):
        return '<Marker>'
marker = Marker()

def parse(config, schema=None, transform=None, process=True):
    "Parse a configuration"
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
