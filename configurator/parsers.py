from collections import defaultdict


class ParseError(Exception):
    """
    The exception raised when an appropriate parser cannot be found for a config
    stream.
    """


class Parsers(defaultdict):

    supported = {
        'json': ('json', 'load'),
        'toml': ('toml', 'load'),
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
