from testfixtures import compare

from configurator import Config
from configurator.patterns import load_with_extends


def test_load_with_extends_key_not_present(dir):
    path = dir.write('file.json', '{"key":"value"}')
    compare(load_with_extends(path, key='extends'), expected=Config({'key': 'value'}))
