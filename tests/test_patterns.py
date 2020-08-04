import json

from testfixtures import compare

from configurator import Config
from configurator.patterns import load_with_extends


class TestLoadWithExtends(object):

    def test_key_not_present(self, dir):
        path = dir.write('file.json', '{"key":"value"}')
        compare(load_with_extends(path, key='extends'), expected=Config({'key': 'value'}))

    def test_root(self, dir):
        path1 = dir.write('file1.json', '{"root": {"f1key":"f1value"}}')
        path2 = dir.write('file2.json', json.dumps({'root': {
            'f2key': 'f2value',
            'extends': path1,
        }}))
        compare(load_with_extends(path2, key='extends', root='root'), expected=Config({
            'f1key': 'k1value',
            'f2key': 'f2value',
        }))
