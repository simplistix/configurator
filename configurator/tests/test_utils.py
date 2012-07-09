# Copyright (c) 2012 Simplistix Ltd
# See license.txt for license details.

from configurator._utils import get_source
from unittest import TestCase

class TestUtils(TestCase):

    def test_get_source(self):
        def level2():
            return get_source()
        def level1():
            return level2()
        if __file__.endswith('.pyc'):
            file = __file__[:-1] # pragma: no cover
        else:
            file = __file__ # pragma: no cover
        self.assertEqual(
            level1(),
            "File %r, line 13, in level1" % file
            )
