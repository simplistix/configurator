# Copyright (c) 2011 Simplistix Ltd
# See license.txt for license details.

from configurator.api import API, Attribute as A, History as H
from configurator.formats.conf import parse
from testfixtures import compare,ShouldRaise,Comparison as C
from unittest import TestCase

class Tests(TestCase):

    def test_simple(self):
        result = parse('test.conf',
                       """
                       key1 value1
                       key2 value2
                       """
                       )
        compare(API(key1=H([A('value1', 'line 2 of test.conf', 'set')]),
                    key2=H([A('value2', 'line 3 of test.conf', 'set')])),result)

    def test_whitespace(self):
        result = parse('test.conf',
                       """
                       key1 value1 value2
                       key2   value3
                       """
                       )
        compare(API(key1=H([A('value1 value2', 'line 2 of test.conf', 'set')]),
                    key2=H([A('value3', 'line 3 of test.conf', 'set')])),result)

    def test_section(self):
        pass

    def test_end_section_before_open(self):
        pass

    def test_nested_sections(self):
        pass

    def test_comments(self):
        # in sections, nested, etc
        pass
    
    def test_include(self):
        pass

    
