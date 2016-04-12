import yaml


class Config(object):

    def __init__(self, path):
        with open(path) as source:
            self.data = yaml.load(source)

    def __getattr__(self, name):
        return self.data[name]

    def __getitem__(self, name):
        raise NotImplementedError()

    def validate(self, schema):
        schema(self.data)

    def merge(self, other):
        self.data.update(other.data)

    def insert(self, key, other):
        raise NotImplementedError()
