from .node import ConfigNode
from .merge import MergeContext


class Config(ConfigNode):

    def merge(self, source, mapping=None, mergers=None):
        if isinstance(source, Config):
            source = source.data
        context = MergeContext(mergers)
        if mapping is None:
            self.data = context.merge(source, self.data)
