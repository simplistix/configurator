from unittest import TestCase, SkipTest

from testfixtures import TempDirectory, compare
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

        config = Config(path1)
        config.merge(path2)
        config.merge(path3)

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
