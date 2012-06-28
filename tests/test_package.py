# Copyright (c) 2012 Simplistix Ltd
# See license.txt for license details.

from configurator import marker
from unittest import TestCase

class TestMarker(TestCase):

    def test_repr(self):
        self.assertEqual(repr(marker), '<Marker>')

    def test_str(self):
        self.assertEqual(str(marker), '<Marker>')
