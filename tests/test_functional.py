import os
from unittest import TestCase, SkipTest

import yaml
from jinja2 import Environment, FileSystemLoader
from testfixtures import TempDirectory, compare, Replace
from voluptuous import Schema

from configurator import Config


class FunctionalTests(TestCase):

    def setUp(self):
        self.dir = TempDirectory()
        self.addCleanup(self.dir.cleanup)

    def test_overlay(self):
        path1 = self.dir.write('etc/myapp.yml', '''
        base: 1
        user: bad
        file: bad
        ''')

        path2 = self.dir.write('home/.myapp.yml', '''
        user: 2
        file: bad-user
        ''')

        path3 = self.dir.write('app.yml', '''
        file: 3
        ''')

        config = Config.from_file(path1)
        config.merge(Config.from_file(path2))
        config.merge(Config.from_file(path3))

        config.validate(Schema({str: int}))

        compare(config.base, expected=1)
        compare(config.user, expected=2)
        compare(config.file, expected=3)

    def test_explicit_extends(self):
        raise SkipTest('not yet')
        path1 = self.dir.write('base.yml', '''
        base: 1
        file: bad
        ''')

        path2 = self.dir.write('app.yml', '''
        extends: {}
        file: 2
        '''.format(path1))

        config = Config(path2)

        config.validate(Schema({
            'extends': config.merge(),
            'base': int,
            'file': int,
        }))

        compare(config.base, expected=1)
        compare(config.file, expected=2)

    def test_include_list(self):
        raise SkipTest('not yet')
        path1 = self.dir.write('other.yml', '''
        - 2
        - 3
        ''')

        path2 = self.dir.write('app.yml', '''
        root:
          - 1
          - include: {}
        '''.format(path1))

        config = Config(path2)

        config.validate(Schema({
            'include': config.merge(),
            'base': int,
            'file': int,
        }))

        compare(config.base, expected=1)
        compare(config.file, expected=2)

    def test_include_dict(self):
        raise SkipTest('not yet')
        pass

    def test_include_dict_duplicate_keys(self):
        raise SkipTest('not yet')
        pass

    def test_templated(self):
        self.dir.write('etc/myapp.yml', '''
        {% set base = dict(one=1)%}
        base_template: {{ base.one }}
        base_env: {{ MYVAR }}
        file_template: bad
        file_env: bad
        ''')

        self.dir.write('app.yml', '''
        {% set local=2 %}
        file_template: {{ local }}
        file_env: {{ MYVAR }}
        ''')

        with Replace('os.environ.MYVAR', 'hello', strict=False) as r:
            env = Environment(loader=FileSystemLoader(self.dir.path))
            config = None
            context = dict(os.environ)
            for path in 'etc/myapp.yml', 'app.yml':
                text = env.get_template(path).render(context)
                layer = Config.from_text(text)
                if config is None:
                    config = layer
                else:
                    config.merge(layer)

        compare(config.base_template, expected=1)
        compare(config.base_env, expected='hello')
        compare(config.file_template, expected=2)
        compare(config.file_env, expected='hello')
