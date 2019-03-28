from textwrap import dedent

from testfixtures import compare, ShouldRaise

from configurator.node import ConfigNode


class TestInstantiation(object):

    def test_empty(self):
        config = ConfigNode()
        compare(config.data, expected={})

    def test_dict(self):
        config = ConfigNode(dict(x=1))
        compare(config['x'], expected=1)

    def test_list(self):
        config = ConfigNode([1, 2])
        compare(config[0], expected=1)
        compare(config[1], expected=2)
        compare(list(config), expected=[1, 2])

    def test_int(self):
        # not very useful, but documents .data as a public api
        config = ConfigNode(1)
        compare(config.data, 1)


class TestDictAccess(object):

    def test_there_dict(self):
        config = ConfigNode({'foo': 1})
        compare(config['foo'], expected=1)

    def test_there_list(self):
        config = ConfigNode([1])
        compare(config[0], expected=1)

    def test_not_there_dict(self):
        config = ConfigNode({})
        with ShouldRaise(KeyError('foo')):
            config['foo']

    def test_not_there_list(self):
        config = ConfigNode([])
        with ShouldRaise(IndexError('list index out of range')):
            config[0]

    def test_not_there_simple(self):
        config = ConfigNode(1)
        with ShouldRaise(KeyError('foo')):
            config['foo']

    def test_get(self):
        config = ConfigNode({'foo': 1})
        compare(config.get('foo'), expected=1)

    def test_get_default(self):
        config = ConfigNode({})
        compare(config.get('foo', 1), expected=1)

    def test_get_default_default(self):
        config = ConfigNode({})
        compare(config.get('foo'), expected=None)

    def test_get_list_number_key(self):
        config = ConfigNode([1])
        compare(config.get(0), expected=1)

    def test_get_list_string_key(self):
        config = ConfigNode([1])
        compare(config.get('foo'), expected=None)

    def test_simple_value(self):
        config = ConfigNode({})
        compare(config.get('foo', 1), expected=1)

    def test_dict_value(self):
        config = ConfigNode({'foo': {'bar': 1}})
        obj = config['foo']
        assert isinstance(obj, ConfigNode)
        compare(obj.data, expected={'bar': 1})

    def test_list_value(self):
        config = ConfigNode({'foo': [1]})
        obj = config['foo']
        assert isinstance(obj, ConfigNode)
        compare(obj.data, expected=[1])

    def test_get_wrapped_value(self):
        config = ConfigNode({'foo': {'bar': 1}})
        obj = config['foo']
        assert isinstance(obj, ConfigNode)
        compare(obj.data, expected={'bar': 1})

    def test_items_dict(self):
        config = ConfigNode({'foo': 1, 'bar': 2})
        compare(config.items(), expected=[('bar', 2), ('foo', 1)])

    def test_items_list(self):
        config = ConfigNode([])
        expected = "'list' object has no attribute 'items'"
        with ShouldRaise(AttributeError(expected)):
            tuple(config.items())

    def test_items_wrapped_value(self):
        config = ConfigNode({'foo': [1]})
        obj = tuple(config.items())[0][1]
        assert isinstance(obj, ConfigNode)
        compare(obj.data, expected=[1])

    def test_set_item(self):
        config = ConfigNode()
        with ShouldRaise(TypeError):
            config['foo'] = 1
        compare(config.data, expected={})


class TestAttributeAccess(object):

    def test_there(self):
        config = ConfigNode({'foo': 1})
        compare(config.foo, expected=1)

    def test_not_there(self):
        config = ConfigNode({})
        with ShouldRaise(AttributeError('foo')):
            config.foo

    def test_simple_value(self):
        config = ConfigNode({'foo': 1})
        compare(config.foo, expected=1)

    def test_dict_value(self):
        config = ConfigNode({'foo': {'bar': 1}})
        obj = config.foo
        assert isinstance(obj, ConfigNode)
        compare(obj.data, expected={'bar': 1})

    def test_list_value(self):
        config = ConfigNode({'foo': [1]})
        obj = config.foo
        assert isinstance(obj, ConfigNode)
        compare(obj.data, expected=[1])

    def test_name_clash_with_real_attrs(self):
        # method, data, __method
        config = ConfigNode({'get': 1})
        compare(config.get('get'), expected=1)

    def test_list_source(self):
        config = ConfigNode([1])
        with ShouldRaise(AttributeError('foo')):
            config.foo

    def test_simple_source(self):
        config = ConfigNode(1)
        with ShouldRaise(AttributeError('foo')):
            config.foo

    def test_set_attr(self):
        config = ConfigNode()
        with ShouldRaise(AttributeError):
            config.foo = 1
        compare(config.data, expected={})


class TestOtherFunctionality(object):

    def test_iterate_over_list_of_dicts(self):
        node = ConfigNode([{'x': 1}])
        compare(tuple(node)[0], expected=ConfigNode({'x': 2}))

    def test_repr(self):
        node = ConfigNode({'some long key': 'some\nvalue',
                            'another long key': 2,
                            'yet another long key': 3})
        compare(repr(node), expected=dedent("""\
            configurator.node.ConfigNode(
            {'another long key': 2,
             'some long key': 'some\\nvalue',
             'yet another long key': 3}
            )"""))
