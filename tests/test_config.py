from testfixtures import compare, ShouldRaise
from configurator import Config, default_mergers
from .compat import type_error


class TestNodeBehaviour(object):

    def test_dict_access(self):
        config = Config({'foo': 'bar'})
        compare(config['foo'], expected='bar')

    def test_attr_access(self):
        config = Config({'foo': 'bar'})
        compare(config.foo, expected='bar')


class TestMergeTests(object):

    def test_empty_config(self):
        config = Config()
        config.merge(Config())
        compare(config.data, expected={})

    def test_non_empty_config(self):
        config = Config({'foo': 'bar'})
        config.merge(Config({'baz': 'bob'}))
        compare(config.data, {'foo': 'bar', 'baz': 'bob'})

    def test_simple_type(self):
        config = Config()
        with ShouldRaise(type_error(
            "Cannot merge <class 'str'> with <class 'dict'>"
        )):
            config.merge('foo')

    def test_dict_to_dict(self):
        config = Config({'x': 1})
        config.merge({'y': 2})
        compare(config.data, expected={'x': 1, 'y': 2})

    def test_list_to_list(self):
        config = Config([1, 2])
        config.merge([3, 4])
        compare(config.data, expected=[1, 2, 3, 4])

    def test_dict_to_list(self):
        config1 = Config([1, 2])
        config2 = Config({'x': 1})
        with ShouldRaise(type_error(
            "Cannot merge <class 'dict'> with <class 'list'>"
        )):
            config1.merge(config2)

    def test_list_to_dict(self):
        config1 = Config({'x': 1})
        config2 = Config([1, 2])
        with ShouldRaise(type_error(
            "Cannot merge <class 'list'> with <class 'dict'>"
        )):
            config1.merge(config2)

    def test_other_to_dict(self):
        config1 = Config(1)
        config2 = Config(1)
        with ShouldRaise(type_error(
            "Cannot merge <class 'int'> with <class 'int'>"
        )):
            config1.merge(config2)

    def test_nested_working(self):
        config1 = Config(dict(x=1, y=[2, 3], z=dict(a=4, b=5)))
        config2 = Config(dict(w=6, y=[7], z=dict(b=8, c=9)))
        config1.merge(config2)

        compare(config1.data,
                expected=dict(x=1, w=6, y=[2, 3, 7], z=dict(a=4, b=8, c=9)))

    def test_override_type_mapping(self):
        config1 = Config([1, 2])
        config2 = Config([3, 4])
        def zipper(context, source, target):
            return zip(target, source)
        config1.merge(config2, mergers={list: zipper})
        compare(config1.data, expected=[(1, 3), (2, 4)])

    def test_type_returns_new_object(self):
        config1 = Config((1, 2))
        config2 = Config((3, 4))
        def concat(context, source, target):
            return target + source
        config1.merge(config2, mergers={tuple: concat})
        compare(config1.data, expected=(1, 2, 3, 4))

    def test_blank_type_mapping(self):
        config1 = Config({'foo': 'bar'})
        config2 = Config({'baz': 'bob'})
        with ShouldRaise(type_error(
            "Cannot merge <class 'dict'> with <class 'dict'>"
        )):
            config2.merge(config1, mergers={})

    def test_supplement_type_mapping(self):
        config1 = Config({'x': (1, 2)})
        config2 = Config({'x': (3, 4)})
        def concat(context, source, target):
            return target + source
        config1.merge(config2, mergers=default_mergers+{tuple: concat})
        compare(config1.data, expected={'x': (1, 2, 3, 4)})

    def test_mapping_paths(self):
        config = Config({'x': 'old'})
        data = {'foo': 'bar'}
        config.merge(data, mapping={
            source['foo']: target['x']
        })
        compare(config.data, expected={'x': 'bar'})

    def test_mapping_strings(self):
        config = Config({'x': 'old'})
        data = {'foo': 'bar'}
        config.merge(data, mapping={
            'foo': 'x'
        })
        compare(config.data, expected={'x': 'bar'})

    def test_mapping_dotted_strings(self):
        config = Config({'a': {'b': 'old'}})
        data = {'c': {'d': 'new'}}
        config.merge(data, mapping={
            'c.d': 'a.b'
        })
        compare(config.data, expected={'a': {'b': 'new'}})

    def test_mapping_type_conversion(self):
        config = Config({'x': 0})
        data = {'y': '1'}
        config.merge(data, mapping={
            convert(source['y'], int): target['x']
        })
        compare(config.data, expected={'x': 1})

    def test_mapping_extensive_conversation(self):
        config = Config({'a': 0})
        data = {'x': 2, 'y': -1}

        def best(possible):
            return max(possible.values())

        config.merge(data, mapping={
            convert(source, best): target['a']
        })

        compare(config.data, expected={'a': 2})


class TestAddition(object):

    def test_top_level_dict(self):
        config1 = Config({'foo': 'bar'})
        config2 = Config({'baz': 'bob'})
        config3 = config1 + config2
        compare(config1.data, {'foo': 'bar'})
        compare(config2.data, {'baz': 'bob'})
        compare(config3.data, {'foo': 'bar', 'baz': 'bob'})

    def test_top_level_list(self):
        config1 = Config([1, 2])
        config2 = Config([3, 4])
        config3 = config1 + config2
        compare(config1.data, [1, 2])
        compare(config2.data, [3, 4])
        compare(config3.data, [1, 2, 3, 4])

    def test_non_config_rhs(self):
        config = Config({'foo': 'bar'}) + {'baz': 'bob'}
        compare(config.data, {'foo': 'bar', 'baz': 'bob'})

    def test_failure(self):
        with ShouldRaise(type_error(
            "Cannot merge <class 'int'> with <class 'dict'>"
        )):
            Config({'foo': 'bar'}) + 1
