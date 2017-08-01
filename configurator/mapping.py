from functools import partial
from operator import itemgetter, attrgetter


class LoadPath(object):

    def __init__(self, *ops):
        self.ops = ops

    def _extend(self, op):
        return type(self)(*(self.ops + (op,)))

    def __getitem__(self, name):
        return self._extend(itemgetter(name))

    def __getattr__(self, name):
        return self._extend(attrgetter(name))


source = LoadPath()


def resolve_text_path(text, data):
    for part in text.split('.'):
        getitem = getattr(data, '__getitem__', None)
        if getitem is None:
            data = getattr(data, part)
        else:
            data = getitem(part)
    return data


def parse_text(segment):
    if isinstance(segment, str):
        segment = LoadPath(partial(resolve_text_path, segment))
    return segment


def load(path, data):
    path = parse_text(path)
    for op in path.ops:
        data = op(data)
    return data


def convert(source, callable_):
    source = parse_text(source)
    return source._extend(callable_)
