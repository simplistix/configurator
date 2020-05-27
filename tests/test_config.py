from ast import literal_eval
from tempfile import NamedTemporaryFile

import pickle
import pytest

from configurator import Config, default_mergers
from io import StringIO
from configurator.parsers import ParseError
from configurator.mapping import source, target, convert, value
from testfixtures import compare, ShouldRaise, TempDirectory, Replace

from .compat import type_error


def python_literal(stream):
    return literal_eval(stream.read())


class TestInstantiation(object):

    def test_empty(self):
        config = Config()
        compare(config.data, expected={})

    def test_dict(self):
        config = Config(dict(x=1))
        compare(config.x, expected=1)

    def test_list(self):
        config = Config([1, 2])
        compare(config[0], expected=1)
        compare(config[1], expected=2)
        compare(list(config), expected=[1, 2])

    def test_int(self):
        # not very useful...
        config = Config(1)
        compare(config.data, expected=1)

    def test_text_string_parser(self):
        config = Config.from_text('{"foo": "bar"}', 'json')
        compare(config.data, expected={'foo': 'bar'})

    def test_bytes_string_parser(self):
        config = Config.from_text(b'{"foo": "bar"}', 'json')
        compare(config.data, expected={'foo': 'bar'})

    def test_text_callable_parser(self):
        config = Config.from_text("{'foo': 'bar'}", python_literal)
        compare(config.data, expected={'foo': 'bar'})

    def test_text_missing_parser(self):
        with ShouldRaise(ParseError("No parser found for 'lolwut'")):
            Config.from_text("{'foo': 'bar'}", 'lolwut')

    def test_path_guess_parser(self):
        with NamedTemporaryFile(suffix='.json') as source:
            source.write(b'{"x": 1}')
            source.flush()
            config = Config.from_path(source.name)
        compare(config.x, expected=1)

    def test_path_guess_parser_no_extension(self):
        with TempDirectory() as dir:
            path = dir.write('nope', b'{"x": 1}')
            with ShouldRaise(ParseError("No parser found for None")):
                Config.from_path(path)

    def test_path_guess_parser_bad_extension(self):
        with NamedTemporaryFile(suffix='.nope') as source:
            with ShouldRaise(ParseError("No parser found for 'nope'")):
                Config.from_path(source.name)

    def test_path_explicit_string_parser(self):
        with NamedTemporaryFile() as source:
            source.write(b'{"x": 1}')
            source.flush()
            config = Config.from_path(source.name, 'json')
        compare(config.x, expected=1)

    def test_path_explicit_callable_parser(self):
        with NamedTemporaryFile() as source:
            source.write(b'{"x": 1}')
            source.flush()
            config = Config.from_path(source.name, python_literal)
        compare(config.x, expected=1)

    def test_path_with_encoding(self):
        with NamedTemporaryFile() as source:
            source.write(b'{"x": "\xa3"}')
            source.flush()
            config = Config.from_path(source.name, 'json', encoding='latin-1')
        compare(config.x, expected=u'\xa3')

    def test_stream_with_name_guess_parser(self):
        with NamedTemporaryFile(suffix='.json') as source:
            source.write(b'{"x": 1}')
            source.flush()
            source.seek(0)
            config = Config.from_stream(source)
        compare(config.x, expected=1)

    def test_stream_no_name_no_parser(self):
        source = StringIO(u'{"x": 1}')
        with ShouldRaise(ParseError("No parser found for None")):
            Config.from_stream(source)

    def test_stream_string_parser(self):
        source = StringIO(u'{"x": 1}')
        config = Config.from_stream(source, 'json')
        compare(config.x, expected=1)

    def test_stream_callable_parser(self):
        source = StringIO(u'{"x": 1}')
        config = Config.from_stream(source, python_literal)
        compare(config.x, expected=1)

    @pytest.fixture()
    def env(self):
        env = {}
        with Replace('os.environ', env):
            yield env

    def test_from_env_single_prefix(self, env):
        env['FOO_BAR'] = 'one'
        env['FOO_BAZ'] = 'two'
        config = Config.from_env(prefix='FOO_')
        compare(config.data, expected={'bar': 'one', 'baz': 'two'})

    def test_from_env_multiple_prefix(self, env):
        env['FOO_BAR'] = 'one'
        env['BOB_BAR'] = 'two'
        config = Config.from_env({'FOO_': 'foo', 'BOB_': 'bob'})
        compare(config.data, expected={
            'foo': {'bar': 'one'},
            'bob': {'bar': 'two'}
        })

    def test_from_env_target_dotted_string(self, env):
        env['FOO_BAR'] = 'one'
        env['FOO_BAZ'] = 'two'
        config = Config.from_env(prefix={'FOO_': 'a.b.c'})
        compare(config.data, expected={
            'a': {'b': {'c': {'bar': 'one', 'baz': 'two'}}}
        })

    def test_from_env_target_path(self, env):
        env['FOO_BAR'] = 'one'
        env['FOO_BAZ'] = 'two'
        config = Config.from_env(prefix={'FOO_': target['a']})
        compare(config.data, expected={
            'a': {'bar': 'one', 'baz': 'two'}
        })

    def test_from_env_type_suffix(self, env):
        env['FOO_BAR'] = '1'
        env['FOO_BAZ'] = '2'
        config = Config.from_env(prefix='FOO_', types={'_BAZ': int})
        compare(config.data, expected={'bar': '1', 'baz': 2})

    def test_from_env_value_is_empty_string(self, env):
        env['FOO_BAR'] = ''
        env['FOO_BAZ'] = ''
        config = Config.from_env(prefix='FOO_', types={'_BAZ': int})
        compare(config.data, expected={})


class TestPushPop(object):

    def test_push_pop(self):
        config = Config({'x': 1, 'y': 2})
        compare(config.x, expected=1)
        compare(config.y, expected=2)
        config.push(Config({'x': 3}))
        compare(config.x, expected=3)
        compare(config.y, expected=2)
        config.pop()
        compare(config.x, expected=1)
        compare(config.y, expected=2)

    def test_push_empty(self):
        config = Config({'x': 1, 'y': 2})
        compare(config.x, expected=1)
        compare(config.y, expected=2)
        config.push(Config({'x': 3}), empty=True)
        compare(config.x, expected=3)
        with ShouldRaise(AttributeError('y')):
            config.y
        config.pop()
        compare(config.x, expected=1)
        compare(config.y, expected=2)

    def test_push_non_config(self):
        config = Config({'x': 1})
        compare(config.x, expected=1)
        config.push({'x': 2})
        compare(config.x, expected=2)

    def test_pop_without_push(self):
        config = Config({'x': 1, 'y': 2})
        with ShouldRaise(IndexError('pop from empty list')):
            config.pop()

    def test_context_manager_push(self):
        config = Config({'x': 1, 'y': 2})
        compare(config.x, expected=1)
        compare(config.y, expected=2)
        with config.push(Config({'x': 3})):
            compare(config.x, expected=3)
            compare(config.y, expected=2)
        compare(config.x, expected=1)
        compare(config.y, expected=2)

    def test_context_manager_push_pathological(self):
        config = Config({'x': 1, 'y': 2})
        compare(config.x, expected=1)
        compare(config.y, expected=2)
        with config.push():
            config.data['a'] = 5
            config.push({'x': 3})
            config.push({'z': 4})
            compare(config.a, expected=5)
            compare(config.x, expected=3)
            compare(config.y, expected=2)
            compare(config.z, expected=4)
        compare(config.x, expected=1)
        compare(config.y, expected=2)
        with ShouldRaise(AttributeError('a')):
            config.a
        with ShouldRaise(AttributeError('z')):
            config.z

    def test_context_manager_push_deep(self):
        config = Config({'x': {'y': 'z'}})
        with config.push():
            config.data['x']['y'] = 'a'
            compare(config.x.y, expected='a')
        compare(config.x.y, expected='z')


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

    def test_mapping_with_merge(self):
        config = Config({'x': {'y': 1}})
        data = {'z': 2}
        config.merge(data, mapping={
            source: target['x'].merge()
        })
        compare(config.data, expected={'x': {'y': 1, 'z': 2}})

    def test_mapping_with_top_level_merge(self):
        config = Config({'x': {'y': 1}})
        data = {'z': 2}
        config.merge(data, mapping={
            source: target.merge()
        })
        compare(config.data, expected={'x': {'y': 1}, 'z': 2})

    def test_mapping_into_empty_dict(self):
        defaults = Config({
            'section1': {},
            'section2': {'nested': {}}
        })
        config = Config()
        config.merge(defaults)
        config.merge({'value': 1}, mapping={'value': 'section1.value'})
        config.merge({'value': 2}, mapping={'value': 'section2.nested.value'})
        compare(config.data, expected={
            'section1': {'value': 1},
            'section2': {'nested': {'value': 2}}
        })
        compare(defaults.data, expected={
            'section1': {},
            'section2': {'nested': {}}
        })

    def test_mapping_only_source(self):
        config = Config()
        config.merge(mapping={
            value(1): 'section1.value',
            value(2): 'section2.nested.value',
        })
        compare(config.data, expected={
            'section1': {'value': 1},
            'section2': {'nested': {'value': 2}}
        })

    def test_clone(self):
        config = Config({'dict': {'a': 1, 'b': 2},
                         'list': [{'c': 3}, {'d': 4}]})
        config_ = config.clone()
        assert config is not config_
        compare(config_.data, expected=config.data)
        assert config.data is not config_.data
        assert config.data['dict'] is not config_.data['dict']
        assert config.data['list'] is not config_.data['list']
        assert config.data['list'][0] is not config_.data['list'][0]
        assert config.data['list'][1] is not config_.data['list'][1]


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


class TestSerialization(object):

    def test_pickle_default_protocol(self):
        config = Config({'foo': [1, 2]})
        data = pickle.dumps(config)
        config_ = pickle.loads(data)
        compare(expected=config, actual=config_)

    def test_pickle_hickest_protocol(self):
        config = Config({'foo': [1, 2]})
        data = pickle.dumps(config, pickle.HIGHEST_PROTOCOL)
        config_ = pickle.loads(data)
        compare(expected=config, actual=config_)
