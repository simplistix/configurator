class ParseError(Exception):
    """
    The exception raised when an appropriate parser cannot be found for a config
    stream.
    """


class Parsers(dict):
    
    @classmethod
    def load_available(cls):
        parsers = cls()
        for suffix, module_name, parser in (
                ('json', 'json', 'load'),
                ('toml', 'toml', 'load'),
                ('yml', 'yaml', 'safe_load'),
                ('yaml', 'yaml', 'safe_load'),
        ):
            try:
                module = __import__(module_name)
            except ImportError:
                # a parser may have soft dependencies,
                # which may not be available.
                pass
            else:
                parsers[suffix] = getattr(module, parser)
        return parsers

    def get(self, extension):
        try:
            return self[extension]
        except KeyError:
            raise ParseError('No parser found for {!r}'.format(extension))
