# Copyright (c) 2012 Simplistix Ltd
# See license.txt for license details.

class ConfiguratorException(Exception):
    "A base class for all Configurator exceptions"

class HistoryError(Exception):
    "An exception raised when there are problems getting history"

class SourceError(Exception):
    "An exception raised when there are problems finding the origin of an attribute"
