from pkg_resources import iter_entry_points


class ParseError(Exception):
    """
    The exception raised when an appropriate parser cannot be found for a config
    stream.
    """


class Parsers(dict):
    
    @classmethod
    def from_entrypoints(cls):
        parsers = cls()
        for entrypoint in iter_entry_points(group='configurator.parser'):
            try:
                parsers[entrypoint.name] = entrypoint.load()
            except ImportError:
                # a package may present entry points based on soft dependencies,
                # which may not be available.
                pass
        return parsers

    def get(self, extension):
        try:
            return self[extension]
        except KeyError:
            raise ParseError('No parser found for {!r}'.format(extension))
