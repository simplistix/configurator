import sys

from collections import defaultdict


class ParseError(Exception):
    """
    The exception raised when an appropriate parser cannot be found for a config
    stream.
    """


if sys.version_info >= (3, 11):
    # stdlib
    _toml_mod = 'tomllib'
else:
    _toml_mod = 'tomli'


class Parsers(defaultdict):

    # file extension: module name, method name
    supported = {
        'json': ('json', 'load'),
        'toml': (_toml_mod, 'load'),
        'yml': ('yaml', 'safe_load'),
        'yaml': ('yaml', 'safe_load'),
    }

    def __missing__(self, extension):
        try:
            module_name, parser_name = self.supported[extension]
        except KeyError:
            raise ParseError('No parser found for {!r}'.format(extension))
        else:
            module = __import__(module_name)
            return getattr(module, parser_name)
