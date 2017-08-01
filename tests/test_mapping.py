from argparse import Namespace

from testfixtures import compare

from configurator.mapping import source, load, convert


class TestSource(object):

    def test_root(self):
        data = {'foo'}
        compare(load(data, source), expected=data)

    def test_getitem(self):
        data = {'foo': 'bar'}
        compare(load(data, source['foo']), expected='bar')

    def test_index(self):
        data = ['a', 'b']
        compare(load(data, source[1]), expected='b')

    def test_attr(self):
        data = Namespace(x=1)
        compare(load(data, source.x), expected=1)

    def test_nested(self):
        data = {'foo': ['a', 'b', Namespace(x=1)]}
        compare(load(data, source['foo'][2].x), expected=1)

    def test_string_item(self):
        data = {'foo': 'bar'}
        compare(load(data, 'foo'), expected='bar')

    def test_string_attr(self):
        data = Namespace(foo='bar')
        compare(load(data, 'foo'), expected='bar')

    def test_string_dotted(self):
        data = {'foo': Namespace(x=1)}
        compare(load(data, 'foo.x'), expected=1)

    def test_convert(self):
        data = Namespace(x='1')
        compare(load(data, convert(source.x, int)), expected=1)

    def test_convert_string(self):
        data = Namespace(x='1')
        compare(load(data, convert('x', int)), expected=1)
