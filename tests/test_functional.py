from argparse import ArgumentParser

from testfixtures import compare
from configurator import Config
from configurator.mapping import target, convert
import pytest


class TestFunctional(object):

    def test_layered(self, dir):
        # defaults
        config = Config({
            'database': {'user': 'foo'},
            'special': False
        })
        # from system file:
        path = dir.write('etc/myapp.json', '{"special": true}')
        config.merge(Config.from_path(path))
        # from user file:
        path = dir.write('home/user/myapp.json', '{"database": {"password": "123"}}')
        config.merge(Config.from_path(path))
        # end result:
        compare(config.database.user, expected='foo')
        compare(config.database.password, expected='123')
        compare(config.special, expected=True)

    def test_defaults_and_argparse(self):
        parser = ArgumentParser()
        parser.add_argument('--first-url')
        parser.add_argument('--attempts', type=int, default=2)
        parser.add_argument('--bool-a', action='store_true')
        parser.add_argument('--bool-b', action='store_false')

        args = parser.parse_args(['--first-url', 'override_url', '--bool-a'])
        compare(args.bool_b, expected=True)

        config = Config({'urls': ['default_url'], 'bool_b': False})

        config.merge(args, {
            'first_url': target['urls'].insert(0),
            'attempts': target['attempts'],
            'bool_a': target['bool_a'],
            'bool_b': target['bool_b'],
        })

        compare(config.urls, expected=['override_url', 'default_url'])
        compare(config.attempts, expected=2)
        compare(config.bool_a, expected=True)
        compare(config.bool_b, expected=True)

    def test_defaults_and_env(self):
        config = Config({'present': 'dp', 'absent': 'da'})

        environ = {'ENV_PRESENT': '1'}

        config.merge(environ, {
            convert('ENV_PRESENT', int): 'present',
            convert('ENV_ABSENT', int): 'absent',
        })

        compare(config.present, expected=1)
        compare(config.absent, expected='da')

    def test_overlay(self, dir):
        pytest.importorskip("yaml")
        path1 = dir.write('etc/myapp.yml', '''
        base: 1
        user: bad
        file: bad
        ''')

        path2 = dir.write('home/.myapp.yml', '''
        user: 2
        file: bad-user
        ''')

        path3 = dir.write('app.yml', '''
        file: 3
        ''')

        config = Config.from_path(path1)
        config.merge(Config.from_path(path2))
        config.merge(Config.from_path(path3))

        compare(config.base, expected=1)
        compare(config.user, expected=2)
        compare(config.file, expected=3)


def test_fake_fs(fs):
    fs.create_file('/foo/bar.yml', contents='foo: 1\n')
    config = Config.from_path('/foo/bar.yml')
    compare(config.foo, expected=1)
