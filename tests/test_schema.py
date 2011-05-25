# Copyright (c) 2011 Simplistix Ltd
# See license.txt for license details.

from unittest import TestCase
from testfixtures import compare,ShouldRaise,Comparison as C

class Tests(TestCase):

    def setUp(self):
        return
        from configurator.schema import SchemaSection
        self.s = Section()

    def test_attribute_definition(self):
        return
        self.s.myfield = myfield = Section()
        myfield.type = 'configurator.types.integer'
        myfield.x =1

    def test_section_definition(self):
        # allowed attributes?
        # quantity?
        # type?
        #
        pass
