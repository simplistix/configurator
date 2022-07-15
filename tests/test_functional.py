from argparse import ArgumentParser

from testfixtures import compare, ShouldRaise
from configurator import Config
from configurator.data import DataValue
from configurator.mapping import target, convert
import pytest

from configurator.proxy import Proxy


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

    def test_lazy_load(self, dir):
        yaml = pytest.importorskip("yaml")

        class VaultClient:

            def __init__(self, host, token):
                self.host = host
                self.token = token

            def load(self, key):
                return {'name': key.capitalize(), 'password': '...'}

        class VaultValue(DataValue):

            def __init__(self, client, key):
                self.client = client
                self.key = key

            def get(self):
                return self.client.load(self.key)

        client_ = Proxy()

        def parser(client):

            class Loader(yaml.Loader):
                pass

            def value_from_yaml(loader, node):
                return VaultValue(client, loader.construct_mapping(node)['key'])

            Loader.add_constructor('!from_vault', value_from_yaml)

            def parser_(path):
                return yaml.load(path, Loader)

            return parser_

        parser_ = parser(client_)

        path1 = dir.write('default.yml', '''
            vault:
              host: localhost
              token: foo
            users:
            - !from_vault {key: someuser}
        ''')

        path2 = dir.write('testing.yml', '''
            users:
            - !from_vault {key: testuser}
        ''')

        default = Config.from_path(path1, parser=parser_)
        testing = Config.from_path(path2, parser=parser_)

        # confirm the proxy isn't configured at this point, and so the values can't
        # be resolved without raising an exception:
        with ShouldRaise(RuntimeError('Cannot use proxy before it is configured')):
            default.users[0].name
        with ShouldRaise(RuntimeError('Cannot use proxy before it is configured')):
            testing.users[0].name

        config = default + testing

        client_.set(VaultClient(**config.vault.data))
        compare(config.users[0].data, expected={'name': 'Someuser', 'password': '...'})

        # make sure iteration works:
        compare([user.name for user in config.users], expected=['Someuser', 'Testuser'])

        # make sure clone still works:
        config.clone()
        compare(config.users.data[0], expected=VaultValue(client_, 'someuser'))

    def test_change_proxy_after_clone(self):
        user = Proxy()
        config = Config({'user': user})
        with ShouldRaise(RuntimeError('Cannot use proxy before it is configured')):
            config.user.get()

        config.set_proxy(user, 'a')
        compare(config.user.get(), expected='a')

        config_ = config.clone()
        config_.set_proxy(user, 'b')

        compare(config.user.get(), expected='a')
        compare(config_.user.get(), expected='b')

    def test_proxy_setting_with_merge(self):
        db = Proxy()

        class User(DataValue):

            def __init__(self, db, name):
                self.db = db
                self.name = name

            def get(self):
                db_ = self.db.get()
                return f'{self.name} from {db_}'

        config1 = Config({'users': [User(db, 'a')]})
        config2 = Config({'users': [User(db, 'b')]})

        db.set(0)
        compare(config1.users, expected=['a from 0'])
        compare(config2.users, expected=['b from 0'])

        config1.set_proxy(db, 1)
        config2.set_proxy(db, 2)
        compare(config1.users, expected=['a from 1'])
        compare(config2.users, expected=['b from 2'])

        config3 = config1 + config2
        compare(config1.users, expected=['a from 1'])
        compare(config2.users, expected=['b from 2'])
        compare(config3.users, expected=['a from 1', 'b from 2'])

        config3.set_proxy(db, 3)
        compare(config1.users, expected=['a from 1'])
        compare(config2.users, expected=['b from 2'])
        compare(config3.users, expected=['a from 3', 'b from 3'])


def test_fake_fs(fs):
    fs.create_file('/foo/bar.yml', contents='foo: 1\n')
    config = Config.from_path('/foo/bar.yml')
    compare(config.foo, expected=1)
