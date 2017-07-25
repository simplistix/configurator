from os.path import expanduser

import yaml


class ConfigNode(object):

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
    #
    # def merge(self, other):
    #     if not isinstance(other, Config):
    #         raise TypeError('{!r} is not a Config instance'.format(other))
    #     data = other.data
    #     if type(data) is not type(self.data):
    #         raise TypeError('Cannot merge {} with {}'.format(
    #             type(data), type(self.data)
    #         ))
    #     elif isinstance(data, list):
    #         self.data.extend(data)
    #     elif isinstance(data, dict):
    #         for key, value in other.data.items():
    #             self.data[key] = self._merge(self.data[key])
    #             self.data.update(data)
    #     else:
    #         raise TypeError('Cannot merge {!r}'.format(data))


class Config(ConfigNode):

    def __init__(self, data=None):
        if data is None:
            data = {}
        self.data = data

    @classmethod
    def from_text(cls, text):
        return cls(yaml.load(text))

    @classmethod
    def from_stream(cls, stream):
        return cls(yaml.load(stream))

    @classmethod
    def from_file(cls, path):
        with open(expanduser(path)) as stream:
            return cls.from_stream(stream)


