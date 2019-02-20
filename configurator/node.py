class ConfigNode(object):

    __slots__ = ('data',)

    def __init__(self, data=None):
        if data is None:
            data = {}
        self.data = data

    def _get(self, name):
        try:
            value = self.data[name]
        except TypeError:
            raise KeyError(name)
        if isinstance(value, (dict, list)):
            value = ConfigNode(value)
        return value

    def __getattr__(self, name):
        try:
            return self._get(name)
        except KeyError:
            raise AttributeError(name)

    def __getitem__(self, name):
        return self._get(name)

    def get(self, name, default=None):
        try:
            return self._get(name)
        except KeyError:
            return default

    def items(self):
        for key, value in sorted(self.data.items()):
            if isinstance(value, (dict, list)):
                value = ConfigNode(value)
            yield key, value

    def __iter__(self):
        for item in self.data:
            yield item
