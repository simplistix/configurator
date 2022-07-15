from testfixtures import compare, ShouldRaise, generator

from configurator.data import DataValue
from configurator.mapping import load, source
from configurator.node import ConfigNode


class TestDataValue:

    def test_load_root(self):
        compare(load(DataValue('foo'), source), expected='foo')

    def test_load_nested(self):
        compare(load([DataValue('foo')], source[0]), expected='foo')

    def test_load_traverse_simple(self):
        with ShouldRaise(TypeError('string indices must be integers')):
            load(DataValue('foo'), source['foo'])

    def test_load_traverse_container(self):
        compare(load([DataValue({'bar': ['foo']})], source[0]['bar'][0]), expected='foo')

    def test_item_get_container(self):
        compare(ConfigNode({'a': DataValue({'b': 'c'})})['a'], expected=ConfigNode({'b': 'c'}))

    def test_attr_get_simple(self):
        compare(ConfigNode({'a': DataValue('b')}).a, expected='b')

    def test_items(self):
        compare(ConfigNode({'a': DataValue('b')}).items(), expected=generator(('a', 'b')))

    def test_node_get(self):
        compare(ConfigNode(DataValue('b')).get(), expected='b')

    def test_node_get_name(self):
        compare(ConfigNode({'a': DataValue('b')}).get('a'), expected='b')

    def test_node_get_wrapped(self):
        compare(ConfigNode(DataValue({'b': 'c'})).get(), expected={'b': 'c'})

    def test_node_get_wrapped_name(self):
        compare(ConfigNode({'a': DataValue({'b': 'c'})}).get('a'), expected=ConfigNode({'b': 'c'}))

    def test_node_node_traverse(self):
        node = ConfigNode({'b': DataValue({'c': {'d': 'e'}})})
        compare(node.node('b.c.d').get(), expected='e')
