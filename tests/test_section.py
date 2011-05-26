# Copyright (c) 2011 Simplistix Ltd
# See license.txt for license details.

from unittest import TestCase
from testfixtures import compare,ShouldRaise,Comparison as C

class Tests(TestCase):

    def setUp(self):
        from configurator.section import Section
        self.s = Section()

    # simple access
    
    def test_dict_get_not_there(self):
        compare(self.s.get('foo'),None)

    def test_dict_get_not_there_default(self):
        compare(self.s.get('foo','bar'),'bar')

    def test_dict_getitem(self):
        self.s['foo']='bar'
        compare(self.s['foo'],'bar')

    def test_getattr(self):
        self.s['foo']='bar'
        compare(self.s.foo,'bar')

    def test_getattr_nothere(self):
        with ShouldRaise(AttributeError('foo')):
            self.s.foo

    def test_getattr_default(self):
        compare(getattr(self.s,'foo','bar'),'bar')

    # setting
    
    def test_setattr(self):
        self.s.foo='bar'
        compare(self.s.foo,'bar')
        
    def test_tree(self):
        from configurator.section import Section
        child = Section()
        self.s.child = child
        self.assertTrue(self.s.child is child)
