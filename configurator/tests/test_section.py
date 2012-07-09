# Copyright (c) 2011-2012 Simplistix Ltd
# See license.txt for license details.

from unittest import TestCase
from testfixtures import compare, ShouldRaise, Comparison as C

from configurator import api
from configurator.section import Section

from .common import SourceMixin

class Base(SourceMixin):

    def setUp(self):
        super(Base, self).setUp()
        self.s = Section()
        self.a = api(self.s)

class Tests(Base, TestCase):

    # simple access
    
    def test_dict_get(self):
        self.a.set('foo', 'v')
        compare(self.s.get('foo'), 'v')

    def test_dict_get_none_value(self):
        self.a.set('foo', None)
        compare(self.s.get('foo'), None)

    def test_dict_get_not_there(self):
        compare(self.s.get('foo'), None)

    def test_dict_get_not_there_default(self):
        compare(self.s.get('foo','bar'), 'bar')

    def test_dict_getitem(self):
        self.a.set('foo', 'bar')
        compare(self.s['foo'], 'bar')

    def test_dict_getitem_none_value(self):
        self.a.set('foo', None)
        compare(self.s['foo'], None)

    def test_dict_getitem_not_there(self):
        with ShouldRaise(KeyError('foo')):
            self.s['foo']

    def test_getattr(self):
        self.a.set('foo', 'bar')
        compare(self.s.foo, 'bar')

    def test_getattr_nothere(self):
        with ShouldRaise(AttributeError('foo')):
            self.s.foo

    def test_getattr_default(self):
        compare(getattr(self.s, 'foo', 'bar'), 'bar')

    # simple setting
    
    def test_setattr(self):
        self.s.foo='bar'
        compare(self.a.get('foo').value, 'bar')

    def test_tree(self):
        child = Section()
        self.s.child = child
        self.assertTrue(self.s.child is child)

    def test_set_special_name(self):
        self.s.get = 'foo'
        compare(self.a.get('get').value, 'foo')
        compare(self.s.get('get'), 'foo')
        compare(self.s['get'], 'foo')
        
    # source
    def test_setattr_source(self):
        self.s.foo='bar'
        compare(self.a.source('foo'), 'default_source')

    def test_setitem_source(self):
        self.s['foo']='bar'
        compare(self.a.source('foo'), 'default_source')

    def test_section_source(self):
        s = Section('my source')
        compare(api(s).source(), 'my source')

    def test_section_source_default(self):
        s = Section()
        compare(api(s).source(), 'default_source')

class TestIteration(Base):
    
    # iteration

    def setUp(self):
        super(TestIteration, self).setUp()
        self.a.set('k1', 'v1')
        self.a.append('v2')
        self.a.set('k3', 'v3')
    
    def test_iteration(self):
        compare(['k1', 'k3'], list(self.s))

    def test_iteration_items(self):
        actual = []
        for name, value in self.s.items():
            actual.append((name, value))
        compare([
            ('k1', 'v1'),
            (None, 'v2'),
            ('k3', 'v3'),
            ], actual)
        
    def test_iteration_keys(self):
        compare(['k1', 'k3'], list(self.s.keys()))

    def test_iteration_values(self):
        compare(['v1', 'v2', 'v3'], list(self.s.values()))
