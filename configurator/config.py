import json

from io import open
from os.path import expanduser
from .node import ConfigNode
from .mapping import load, store
from .merge import MergeContext


class ParseError(Exception): pass


class Config(ConfigNode):

    parsers = {
        'json': json.loads,
    }

    @classmethod
    def from_text(cls, text, parser):
        if not callable(parser):
            try:
                parser = cls.parsers[parser]
            except KeyError:
                raise ParseError('No parser found for {!r}'.format(parser))
        return cls(parser(text))

    @classmethod
    def from_stream(cls, stream, parser=None):
        if parser is None:
            name = getattr(stream, 'name', None)
            if name is not None:
                try:
                    _, parser = name.rsplit('.', 1)
                except ValueError:
                    pass
        return cls.from_text(stream.read(), parser)

    @classmethod
    def from_path(cls, path, parser=None, encoding=None):
        with open(expanduser(path), encoding=encoding) as stream:
            return cls.from_stream(stream, parser)

    def merge(self, source, mapping=None, mergers=None):
        if isinstance(source, Config):
            source = source.data
        context = MergeContext(mergers)
        if mapping is None:
            self.data = context.merge(source, self.data)
        else:
            for source_path, target_path in mapping.items():
                value = load(source, source_path)
                self.data = store(self.data, target_path, value, context)

    def __add__(self, other):
        result = Config(type(self.data)())
        result.merge(self)
        result.merge(other)
        return result
