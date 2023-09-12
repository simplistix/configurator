import io

try:
    import tomllib
except ImportError:
    import tomli as tomllib


def load(f, *, parse_float=float):
    # wrapper around tomllib.load to be more forgiving of streams opened in text mode
    if isinstance(f, io.TextIOWrapper):
        return tomllib.load(f.buffer, parse_float=parse_float)
    elif isinstance(f, io.StringIO):
        return tomllib.loads(f.getvalue(), parse_float=parse_float)
    else:
        return tomllib.load(f, parse_float=parse_float)
