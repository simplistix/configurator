# Copyright (c) 2011-2012 Simplistix Ltd
# See license.txt for license details.

from configurator._api import Attribute
from unittest import TestCase
from testfixtures import compare

from .common import SourceMixin

class AttributeTests(SourceMixin, TestCase):

    def _check_eq(self, a, b):
        self.assertTrue(a == b)
        self.assertFalse(a != b)
        
    def _check_not_eq(self, a, b):
        self.assertFalse(a == b)
        self.assertTrue(a != b)
        
    def test_eq(self):
        self._check_eq(
            Attribute('n', 'v', 'a', 's', 0, None),
            Attribute('n', 'v', 'a', 's', 0, None)
            )

    def test_diff_type(self):
        self._check_not_eq(
            Attribute('n', 'v', 'a', 's', 0, None),
            {}
            )
        
    def test_ne_value(self):
        self._check_not_eq(
            Attribute('n', 'v', 'a', 's', 0, None),
            Attribute('n', 'v`' , 'a', 's', 0, None)
            )
        
    def test_ne_source(self):
        self._check_not_eq(
            Attribute('n', 'v', 'a', 's', 0, None),
            Attribute('n', 'v', 'a', 's`', 0, None)
            )
        
    def test_ne_action(self):
        self._check_not_eq(
            Attribute('n', 'v', 'a', 's', 0, None),
            Attribute('n', 'v', 'a`', 's', 0, None)
            )

    def test_ne_name(self):
        self._check_not_eq(
            Attribute('n', 'v', 'a', 's', 0, None),
            Attribute('n`', 'v', 'a', 's', 0, None)
            )
        
    def test_ne_previous(self):
        # previous doesn't matter for equality
        self._check_eq(
            Attribute('n', 'v', 's', 'a', 0, 'p'),
            Attribute('n', 'v', 's', 'a', 0, 'p`')
            )

    def test_ne_index(self):
        # two identical values may be appended,
        # they should not be considered to be
        # the same
        self._check_not_eq(
            Attribute('n', 'v', 'a', 's', 0, None),
            Attribute('n', 'v', 'a', 's', None, 1)
            )
        
    def test_repr(self):
        compare(
            "Attribute('n', 'v', 'a', 's', 0, None)",
            repr(Attribute('n', 'v', 'a', 's', 0, None))
            )

    def test_str(self):
        compare(
            "Attribute(name='n', value='v', action='a', source='s', "
            "index=0, previous=None)",
            str(Attribute(name='n',
                          value='v',
                          action='a',
                          source='s',
                          previous=None,
                          index=0))
            )

    def test_history_empty(self):
        compare(
            [Attribute('n', 'v', 'a', 's', 0, None)],
            Attribute('n', 'v', 'a', 's', 0, None).history()
            )

    def test_history_normal(self):
        a = Attribute('n', 'v1', 'a', 's', 0, None)
        a2 = Attribute('n', 'v2', 'a', 's', 0, a)
        compare(
            [Attribute('n', 'v1', 'a', 's', 0, None),
             Attribute('n', 'v2', 'a', 's', 0, None)],
            a2.history()
            )
