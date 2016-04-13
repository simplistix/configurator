from os.path import expanduser

import yaml


class Config(object):

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

    def __getattr__(self, name):
        return self.data[name]

    def __getitem__(self, name):
        return self.data[name]

    def __iter__(self):
        for item in self.data:
            yield item

    def validate(self, schema):
        schema(self.data)

    def merge(self, other):
        if not isinstance(other, Config):
            raise TypeError('{!r} is not a Config instance'.format(other))
        data = other.data
        if isinstance(self.data, list):
            self.data.extend(data)
        else:
            self.data.update(data)

    def insert(self, key, other):
        raise NotImplementedError()
