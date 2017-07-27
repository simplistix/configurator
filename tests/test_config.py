from testfixtures import compare, ShouldRaise

from configurator import Config, default_mergers



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
        with ShouldRaise(TypeError(
            "Cannot merge <type 'str'> with <type 'dict'>"
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
        with ShouldRaise(TypeError(
            "Cannot merge <type 'dict'> with <type 'list'>"
        )):
            config1.merge(config2)

    def test_list_to_dict(self):
        config1 = Config({'x': 1})
        config2 = Config([1, 2])
        with ShouldRaise(TypeError(
            "Cannot merge <type 'list'> with <type 'dict'>"
        )):
            config1.merge(config2)

    def test_other_to_dict(self):
        config1 = Config(1)
        config2 = Config(1)
        with ShouldRaise(TypeError(
            "Cannot merge <type 'int'> with <type 'int'>"
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
        with ShouldRaise(TypeError(
            "Cannot merge <type 'dict'> with <type 'dict'>"
        )):
            config2.merge(config1, mergers={})

    def test_supplement_type_mapping(self):
        config1 = Config({'x': (1, 2)})
        config2 = Config({'x': (3, 4)})
        def concat(context, source, target):
            return target + source
        config1.merge(config2, mergers=default_mergers+{tuple: concat})
        compare(config1.data, expected={'x': (1, 2, 3, 4)})
