from .node import ConfigNode
from .mapping import load, store
from .merge import MergeContext


class Config(ConfigNode):

    def merge(self, source, mapping=None, mergers=None):
        if isinstance(source, Config):
            source = source.data
        context = MergeContext(mergers)
        if mapping is None:
            self.data = context.merge(source, self.data)
        else:
            for source_path, target_path in mapping.items():
                value = load(source, source_path)
                store(self.data, target_path, value)

    def __add__(self, other):
        result = Config(type(self.data)())
        result.merge(self)
        result.merge(other)
        return result
