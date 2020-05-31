from argparse import Namespace
from testfixtures import compare, ShouldRaise

from configurator.mapping import source, load, convert, store, target, required, if_supplied, value
from configurator.merge import MergeContext
from configurator.path import NotPresent


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

    def test_required_and_present(self):
        data = ['a', 'b']
        compare(load(data, required(source[1])), expected='b')

    def test_getitem_not_present(self):
        data = {}
        with ShouldRaise(NotPresent('foo')):
            load(data, required(source['foo']))

    def test_getitem_nested_not_present(self):
        data = {}
        with ShouldRaise(NotPresent('foo')):
            load(data, required(source['foo']['bar']))

    def test_index_not_present(self):
        data = ['a']
        with ShouldRaise(NotPresent(1)):
            load(data, required(source[1]))

    def test_attr_not_present(self):
        data = Namespace()
        with ShouldRaise(NotPresent('x')):
           load(data, required(source.x))

    def test_attr_nested_not_present(self):
        data = Namespace()
        with ShouldRaise(NotPresent('x')):
           load(data, required(source.x.y))

    def test_getitem_not_present_okay(self):
        data = {}
        compare(load(data, source['foo']), expected=NotPresent('foo'))

    def test_index_not_present_okay(self):
        data = ['a']
        compare(load(data, source[1]), expected=NotPresent(1))

    def test_attr_not_present_okay(self):
        data = Namespace()
        compare(load(data, source.x), expected=NotPresent('x'))

    def test_nested(self):
        data = {'foo': ['a', 'b', Namespace(x=1)]}
        compare(load(data, source['foo'][2].x), expected=1)

    def test_nested_missing_okay(self):
        data = {'foo': []}
        compare(load(data, source['foo'][2].x),
                expected=NotPresent(2))

    def test_string_item(self):
        data = {'foo': 'bar'}
        compare(load(data, 'foo'), expected='bar')

    def test_string_attr(self):
        data = Namespace(foo='bar')
        compare(load(data, 'foo'), expected='bar')

    def test_string_item_not_present(self):
        data = {}
        compare(load(data, 'foo'), expected=NotPresent('foo'))

    def test_string_attr_not_present(self):
        data = Namespace()
        compare(load(data, 'foo'), expected=NotPresent('foo'))

    def test_string_dotted(self):
        data = {'foo': Namespace(x=1)}
        compare(load(data, 'foo.x'), expected=1)

    def test_string_item_not_present_required(self):
        data = {}
        with ShouldRaise(NotPresent('foo')):
            load(data, required('foo'))

    def test_convert(self):
        data = Namespace(x='1')
        compare(load(data, convert(source.x, int)), expected=1)

    def test_convert_string(self):
        data = Namespace(x='1')
        compare(load(data, convert('x', int)), expected=1)

    def test_convert_not_present(self):
        data = {}
        compare(load(data, convert('x', int)), expected=NotPresent('x'))

    def test_insert(self):
        with ShouldRaise(TypeError('Cannot use insert() in source')):
            load(None, source.insert(0))

    def test_append(self):
        with ShouldRaise(TypeError('Cannot use append() in source')):
            load(None, source.append())

    def test_merge(self):
        with ShouldRaise(TypeError('Cannot use merge() in source')):
            load(None, source.merge())

    def test_if_supplied_truthy(self):
        data = Namespace(x='1')
        compare(load(data, if_supplied(source.x)), expected='1')

    def test_if_supplied_false(self):
        data = Namespace(x=False)
        compare(load(data, if_supplied(source.x)), expected=False)

    def test_if_supplied_falsy(self):
        data = Namespace(x=None)
        compare(load(data, if_supplied(source.x)), expected=NotPresent(None))

    def test_if_supplied_string(self):
        data = Namespace(x='1')
        compare(load(data, if_supplied('x')), expected='1')

    def test_if_supplied_empty_string(self):
        data = Namespace(x='')
        compare(load(data, if_supplied('x')), expected=NotPresent(''))

    def test_if_supplied_custom(self):
        data = Namespace(x='Unavailable')
        compare(load(data, if_supplied(source.x, false_values={'Unavailable'})),
                expected=NotPresent('Unavailable'))

    def test_if_supplied_required_falsy(self):
        data = Namespace(x=None)
        with ShouldRaise(NotPresent(None)):
            load(data, required(if_supplied(source.x)))

    def test_if_supplied_str(self):
        compare(str(if_supplied(source.x)), expected='if_supplied(source.x)')

    def test_value(self):
        compare(load(None, value(42)), expected=42)

    def test_value_if_supplied_falsy(self):
        compare(load({}, if_supplied(value(None))), expected=NotPresent(None))


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

    def test_getitem_not_present(self):
        data = {'foo': 'bar'}
        store(data, target['foo'], NotPresent('foo'))
        compare(data, expected={'foo': 'bar'})

    def test_index(self):
        data = ['a', 'b']
        store(data, target[1], 'c')
        compare(data, expected=['a', 'c'])

    def test_index_not_present(self):
        data = ['a', 'b']
        store(data, target[1], NotPresent(1))
        compare(data, expected=['a', 'b'])

    def test_append(self):
        data = ['a', 'b']
        store(data, target.append(), 'c')
        compare(data, expected=['a', 'b', 'c'])

    def test_append_nested(self):
        data = []
        store(data, target.append()['a'], 'b')
        compare(data, expected=[{'a': 'b'}])

    def test_append_not_present(self):
        data = []
        store(data, target.append()['a'], NotPresent('foo'))
        compare(data, expected=[{}])

    def test_insert(self):
        data = ['a', 'b']
        store(data, target.insert(1), 'c')
        compare(data, expected=['a', 'c', 'b'])

    def test_insert_nested(self):
        data = []
        store(data, target.insert(0)['a'], 'b')
        compare(data, expected=[{'a': 'b'}])

    def test_insert_not_present(self):
        data = []
        store(data, target.insert(0)['a'], NotPresent('foo'))
        compare(data, expected=[{}])

    def test_attr(self):
        data = Namespace(x=1)
        store(data, target.x, 2)
        compare(data.x, 2)

    def test_attr_not_present(self):
        data = Namespace(x=1)
        store(data, target.x, NotPresent('foo'))
        compare(data.x, 1)

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

    def test_set_on_required(self):
        data = '1'
        with ShouldRaise(TypeError('Cannot use required() as target')):
            store(data, required(target), 'y')

    def test_ensure_on_required(self):
        data = '1'
        with ShouldRaise(TypeError('Cannot use required() as target')):
            store(data, required(target).x, 'y')

    def test_set_on_supplied(self):
        data = '1'
        with ShouldRaise(TypeError('Cannot use if_supplied() as target')):
            store(data, if_supplied(target), 'y')

    def test_ensure_on_supplied(self):
        data = '1'
        with ShouldRaise(TypeError('Cannot use if_supplied() as target')):
            store(data, if_supplied(target).x, 'y')

    def test_merge(self):
        data = {'x': 1}
        data = store(data, target.merge(), {'y': 2}, MergeContext())
        compare(data, expected={'x': 1, 'y': 2})

    def test_merge_nested(self):
        data = {'x': {'y': 2}}
        store(data, target['x'].merge(), {'z': 1}, MergeContext())
        compare(data, expected={'x': {'y': 2, 'z': 1}})

    def test_merge_not_present(self):
        data = {'x': {'y': 2}}
        store(data, target['x'].merge(), NotPresent('foo'), MergeContext())
        compare(data, expected={'x': {'y': 2}})

    def test_ensure_on_merge(self):
        data = {}
        with ShouldRaise(TypeError('merge() must be final operation')):
            store(data, target.merge().x, 'y', MergeContext())
