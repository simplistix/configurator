from os.path import expanduser

import yaml


class Config(object):

    def _load(self, source):
        if isinstance(source, basestring):
            with open(expanduser(source)) as stream:
                return yaml.load(stream)
        elif source is None:
            return {}
        elif getattr(source, 'read', None):
                return yaml.load(source.read())
        elif isinstance(source, (dict, list)):
            return source
        else:
            raise ValueError(
                'source cannot be of type {}: {}'.format(type(source), source)
            )

    def __init__(self, source=None):
        self.data = self._load(source)

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
        data = self._load(other)
        if isinstance(self.data, list):
            self.data.extend(data)
        else:
            self.data.update(data)

    def insert(self, key, other):
        raise NotImplementedError()
