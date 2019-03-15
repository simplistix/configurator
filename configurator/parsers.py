from pkg_resources import iter_entry_points


def load_parsers():
    parsers = {}
    for entrypoint in iter_entry_points(group='configurator.parser'):
        try:
            parsers[entrypoint.name] = entrypoint.load()
        except ImportError:
            # a package may present entry points based on soft dependencies,
            # which may not be available.
            pass
    return parsers
