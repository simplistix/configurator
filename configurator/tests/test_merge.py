# Copyright (c) 2011-2012 Simplistix Ltd
# See license.txt for license details.

from configurator import api
from configurator._api import API, Attribute
from configurator.section import Section
from unittest import TestCase
from testfixtures import compare

from .common import SourceMixin

from nose import SkipTest
raise SkipTest()

class MergeTests(SourceMixin, TestCase):

    def setUp(self):
        super(APITests, self).setUp()
        self.sec_a = Section()
        
        self.a = API(self.section, 'the name', None)

    def test_merge_section(self):
        self.a.set('anb', 'a not b')
        self.a.set('mod', 'from a')
        self.a.remove('rema')
        self.a.set('remb', 'bad')
        self.a.append('a value')

        sb = Section()
        b = api(sb)
        b.set('bna', 'b not a')
        b.set('mod', 'from b')
        b.set('rema', 'good')
        b.remove('remb')
        b.append('b value')

        self.a.merge(sb)

        compare(Attribute('anb', 'a not b', 'set', 'default_source3', 0, None),
                self.a.get('anb'))
        compare([Attribute('anb', 'a not b', 'set', 'default_source3', 0, None)],
                self.a.history(name='anb'))
        
        compare(Attribute('mod', 'from b', 'set', 'default_source3', 1, None),
                self.a.get('mod'))
        compare([
            Attribute('mod', 'from a', 'set', 'default_source3', 1, None),
            Attribute('mod', 'from b', 'set', 'default_source3', 1, None)
            ], self.a.history(name='mod'))
        
        compare(Attribute('bna', 'b not a', 'set', 'default_source3', 5, None),
                self.a.get('bna'))
        compare([Attribute('bna', 'b not a', 'set', 'default_source3', 5, None)],
                self.a.history(name='bna'))
        
        compare(Attribute('rema', 'good', 'set', 'default_source3', 2, None),
                self.a.get('rema'))
        compare([
            Attribute('rema', marker, 'remove', 'default_source3', 2, None),
            Attribute('rema', 'good', 'set', 'default_source3', 2, None)
            ],  self.a.history(name='rema'))
        
        compare(marker, self.a.get('remb'))
        compare([
            Attribute('remb', 'bad', 'set', 'default_source3', 3, None),
            Attribute('remb', marker, 'remove', 'default_source3', 3, None),
            ], self.a.history(name='remb'))
        
        compare([
            Attribute('anb', 'a not b', 'set', 'default_source3', 0, None),
            Attribute('mod', 'from b', 'set', 'default_source3', 1, None),
            Attribute('rema', 'good', 'set', 'default_source3', 2, None),
            Attribute(None, 'a value', 'append', 'default_source3', 4, None),            
            Attribute('bna', 'b not a', 'set', 'default_source3', 5, None),
            Attribute(None, 'b value', 'append', 'default_source3', 6, None),            
            ], self.a.items())
        compare([
            Attribute('anb', 'a not b', 'set', 'default_source3', 0, None),
            Attribute('mod', 'from a', 'set', 'default_source3', 1, None),
            Attribute('rema', marker, 'remove', 'default_source3', 2, None),
            Attribute('remb', 'bad', 'set', 'default_source3', 3, None),
            Attribute(None, 'a value', 'append', 'default_source3', 4, None),
            Attribute('bna', 'b not a', 'set', 'default_source3', 5, None),
            Attribute('mod', 'from b', 'set', 'default_source3', 1, None),
            Attribute('rema', 'good', 'set', 'default_source3', 2, None),
            Attribute('remb', marker, 'remove', 'default_source3', 3, None),
            Attribute(None, 'b value', 'append', 'default_source3', 6, None),            
            ], self.a.history())

    def test_merge_api(self):
        self.a.set('a', 'a')
        sec_b = Section()
        b = api(sec_b)
        b.set('b', 'b')
        self.a.merge(b)
        compare(self.a.get('a').value, 'a')
        compare(self.a.get('b').value, 'b')
        
    def test_merge_other(self):
        with ShouldRaise(TypeError('Can only merge Section or API instances')):
            self.a.merge(object())

    def test_merge_nested_a_not_b(self):
        b = Section()
        b_a = api(b)
        # sec in a not b
        a_sub = Section()
        a_sub_a = api(a_sub)
        a_sub_a.set('id', 'a')
        self.a.set('sub', a_sub)

    def test_merge_nested_a_not_b_unamed(self):
        b = Section()
        b_a = api(b)
        # sec in a not b
        a_sub = Section()
        a_sub_a = api(a_sub)
        a_sub_a.set('id', 'a')
        self.a.append(a_sub)

    def test_merge_nested_b_not_a(self):
        b = Section()
        b_a = api(b)
        # sec in b not a
        b_sub = Section()
        b_sub_a = api(b_sub)
        bnota_a.set('id', 'b')
        b_a.set('sub', b_sub)

    def test_merge_nested_b_not_a_unamed(self):
        b = Section()
        b_a = api(b)
        # sec in b not a
        b_sub = Section()
        b_sub_a = api(b_sub)
        bnota_a.set('id', 'b')
        b_a.append(b_sub)
        
    def test_merge_nested_in_both(self):
        b = Section()
        b_a = api(b)
        # sec in both, merge:
        aboth = Section()
        aboth_a = api(aboth)
        aboth_a.set('id', 'aboth')
        aboth_a.set('a', 'a')
        self.a.set('both', aboth)
        bboth = Section()
        bboth_a = api(bboth)
        bboth_a.set('id', 'bboth')
        bboth_a.set('b', 'b')
        b_a.set('both', bboth)

    def test_merge_nested_in_both_with_replace(self):
        b = Section()
        b_a = api(b)
        # sec in both, merge:
        aboth = Section()
        aboth_a = api(aboth)
        aboth_a.set('id', 'aboth')
        aboth_a.set('a', 'a')
        self.a.set('both', aboth)
        bboth = Section()
        bboth_a = api(bboth)
        bboth_a.set('id', 'bboth')
        bboth_a.set('b', 'b')
        b_a.replace('both', bboth)

    """
        self.a.merge(b)

        compare([
            ], self.a.items())
        compare([
            ], self.a.history())
        compare(self.a.get('anotb').value.id, 'anotb')
        compare(self.a.get('bnota').value.id, 'bnota')
        compare([
            ], api(self.a.get('anotb').value).items())
        compare([
            ], api(self.a.get('bnota').value).items())
        compare([
            ], api(self.a.get('both').value).items())
        compare([
            ], api(self.a.get('bothr').value).items())
        compare(self.a.get('both').value.id, 'bboth')
        compare(self.a.get('both').value.a, 'a')
        compare(self.a.get('both').value.b, 'b')
        """
        
    def merge_nested_section_and_value(self):
        # the one merged in stomps!
        pass

    def merge_nested_section_and_remove_section(self):
        # removes section :-)
        pass
