from argparse import Namespace

from testfixtures import compare

from configurator.mapping import source, load, convert


class TestSource(object):

    def test_root(self):
        data = {'foo'}
        compare(load(source, data), expected=data)

    def test_getitem(self):
        data = {'foo': 'bar'}
        compare(load(source['foo'], data), expected='bar')

    def test_index(self):
        data = ['a', 'b']
        compare(load(source[1], data), expected='b')

    def test_attr(self):
        data = Namespace(x=1)
        compare(load(source.x, data), expected=1)

    def test_nested(self):
        data = {'foo': ['a', 'b', Namespace(x=1)]}
        compare(load(source['foo'][2].x, data), expected=1)

    def test_string_item(self):
        data = {'foo': 'bar'}
        compare(load('foo', data), expected='bar')

    def test_string_attr(self):
        data = Namespace(foo='bar')
        compare(load('foo', data), expected='bar')

    def test_string_dotted(self):
        data = {'foo': Namespace(x=1)}
        compare(load('foo.x', data), expected=1)

    def test_convert(self):
        data = Namespace(x='1')
        compare(load(convert(source.x, int), data), expected=1)

    def test_convert_string(self):
        data = Namespace(x='1')
        compare(load(convert('x', int), data), expected=1)
