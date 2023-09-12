from collections import defaultdict
from importlib import import_module


class ParseError(Exception):
    """
    The exception raised when an appropriate parser cannot be found for a config
    stream.
    """


class Parsers(defaultdict):

    # file extension: module name, method name
    supported = {
        'json': ('json', 'load'),
        'toml': ('configurator._toml', 'load'),
        'yml': ('yaml', 'safe_load'),
        'yaml': ('yaml', 'safe_load'),
    }

    def __missing__(self, extension):
        try:
            module_name, parser_name = self.supported[extension]
        except KeyError:
            raise ParseError('No parser found for {!r}'.format(extension))
        else:
            module = import_module(module_name)
            return getattr(module, parser_name)
