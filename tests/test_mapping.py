from argparse import Namespace
from testfixtures import compare, ShouldRaise

from configurator.mapping import source, load, convert, store, target
from configurator.merge import MergeContext


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

    def test_insert(self):
        with ShouldRaise(TypeError('Cannot use insert() in source')):
            load(None, source.insert(0))

    def test_append(self):
        with ShouldRaise(TypeError('Cannot use append() in source')):
            load(None, source.append())

    def test_merge(self):
        with ShouldRaise(TypeError('Cannot use merge() in source')):
            load(None, source.merge())


class TestTarget(object):

    def test_root(self):
        data = {'foo'}
        with ShouldRaise(TypeError('Cannot store at root')):
            store(data, target, 'foo')
        compare(data, expected={'foo'})

    def test_getitem(self):
        data = {'foo': 'bar'}
        store(data, target['foo'], 'baz')
        compare(data, expected={'foo': 'baz'})

    def test_index(self):
        data = ['a', 'b']
        store(data, target[1], 'c')
        compare(data, expected=['a', 'c'])

    def test_append(self):
        data = ['a', 'b']
        store(data, target.append(), 'c')
        compare(data, expected=['a', 'b', 'c'])

    def test_append_nested(self):
        data = []
        store(data, target.append()['a'], 'b')
        compare(data, expected=[{'a': 'b'}])

    def test_insert(self):
        data = ['a', 'b']
        store(data, target.insert(1), 'c')
        compare(data, expected=['a', 'c', 'b'])

    def test_insert_nested(self):
        data = []
        store(data, target.insert(0)['a'], 'b')
        compare(data, expected=[{'a': 'b'}])

    def test_attr(self):
        data = Namespace(x=1)
        store(data, target.x, 2)
        compare(data.x, 2)

    def test_nested(self):
        data = {'foo': ['a', 'b', Namespace(x=1)]}
        store(data, target['foo'][2].x, 2)
        compare(data['foo'][2].x, expected=2)

    def test_string_item(self):
        data = {'foo': 'bar'}
        store(data, 'foo', 'baz')
        compare(data, expected={'foo': 'baz'})

    def test_string_attr(self):
        data = Namespace(foo='bar')
        store(data, target.x, 2)
        compare(data.x, 2)

    def test_string_dotted(self):
        data = {'foo': Namespace(x=1)}
        store(data, 'foo.x', 2)
        compare(data['foo'].x, expected=2)

    def test_create_nested_dicts(self):
        # created needed dicts
        data = {}
        store(data, target['x']['y'], 2)
        compare(data, expected={'x': {'y': 2}})

    def test_create_nested_attrs(self):
        # exception
        data = {}
        with ShouldRaise(AttributeError("'dict' object has no attribute 'x'")):
            store(data, target.x.y, 2)

    def test_create_from_dotted_string(self):
        data = {}
        store(data, 'x.y', 2)
        compare(data, expected={'x': {'y': 2}})

    def test_create_nested_attrs_from_dotted_string(self):
        # exception
        data = Namespace()
        with ShouldRaise(AttributeError(
            "'Namespace' object has no attribute 'x'"
        )):
            store(data, 'x.y', 2)

    def test_set_on_convert(self):
        data = '1'
        with ShouldRaise(TypeError('Cannot use convert() as target')):
            store(data, convert(target, int), 'y')

    def test_ensure_on_convert(self):
        data = '1'
        with ShouldRaise(TypeError('Cannot use convert() as target')):
            store(data, convert(target, int).x, 'y')

    def test_merge(self):
        data = {'x': 1}
        data = store(data, target.merge(), {'y': 2}, MergeContext())
        compare(data, expected={'x': 1, 'y': 2})

    def test_merge_nested(self):
        data = {'x': {'y': 2}}
        store(data, target['x'].merge(), {'z': 1}, MergeContext())
        compare(data, expected={'x': {'y': 2, 'z': 1}})

    def test_ensure_on_merge(self):
        data = {}
        with ShouldRaise(TypeError('merge() must be final operation')):
            store(data, target.merge().x, 'y', MergeContext())