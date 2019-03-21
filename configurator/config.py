from io import open, StringIO
from os.path import exists, expanduser
from .node import ConfigNode
from .mapping import load, store
from .merge import MergeContext
from .parsers import Parsers


class Config(ConfigNode):

    parsers = Parsers.from_entrypoints()

    @classmethod
    def from_text(cls, text, parser, encoding='ascii'):
        if isinstance(text, bytes):
            text = text.decode(encoding)
        return cls.from_stream(StringIO(text), parser)

    @classmethod
    def from_stream(cls, stream, parser=None):
        if parser is None:
            name = getattr(stream, 'name', None)
            if name is not None:
                try:
                    _, parser = name.rsplit('.', 1)
                except ValueError:
                    pass
        if not callable(parser):
            parser = cls.parsers.get(parser)
        return cls(parser(stream))

    @classmethod
    def from_path(cls, path, parser=None, encoding=None, optional=False):
        full_path = expanduser(path)
        if optional and not exists(full_path):
            return cls()
        with open(full_path, encoding=encoding) as stream:
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
