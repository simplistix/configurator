# Copyright (c) 2011 Simplistix Ltd
# See license.txt for license details.

from unittest import TestCase
from testfixtures import compare,ShouldRaise,Comparison as C

class Tests(TestCase):

    def setUp(self):
        from configurator.section import Section
        self.s = Section()

    def test_source_none_specified(self):
        self.s.foo='bar'
        compare(None,self.s._api.source('foo'))
    
    def test_source_none_specified(self):
        self.s._api.set('foo','bar','line 200 - foo.conf')
        compare('line 200 - foo.conf',self.s._api.source('foo'))
        
    def test_history(self):
        from configurator.section import Attribute
        self.s.foo='bar'
        self.s.foo='baz'
        self.s.foo='bob'
        compare([
            C(Attribute('bar',None)),
            C(Attribute('baz',None)),
            C(Attribute('bob',None)),
            ],
            self.s._api.history('foo')
            )
