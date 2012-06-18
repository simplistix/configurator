# Copyright (c) 2011-2012 Simplistix Ltd
# See license.txt for license details.

from configurator import _marker
from configurator.api import API, Attribute, Sequence
from configurator.exceptions import SourceError
from unittest import TestCase
from testfixtures import compare, Comparison as C, ShouldRaise

class AttributeTests(TestCase):

    def test_eq(self):
        self.assertTrue(Attribute('v', 's', 'a')==Attribute('v', 's', 'a'))
        self.assertFalse(Attribute('v', 's', 'a')!=Attribute('v', 's', 'a'))

    def test_diff_type(self):
        self.assertFalse(Attribute('v', 's', 'a')=={})
        self.assertTrue(Attribute('v', 's', 'a')!={})
        
    def test_ne_v(self):
        self.assertFalse(Attribute('v', 's', 'a')==Attribute('v`' , 's', 'a'))
        self.assertTrue(Attribute('v', 's', 'a')!=Attribute('v`' , 's', 'a'))
        
    def test_ne_s(self):
        # source doesn't matter for equality
        self.assertTrue(Attribute('v', 's', 'a')==Attribute('v', 's`', 'a'))
        self.assertFalse(Attribute('v', 's', 'a')!=Attribute('v', 's`', 'a'))
        
    def test_ne_a(self):
        self.assertFalse(Attribute('v', 's', 'a')==Attribute('v', 's', 'a`'))
        self.assertTrue(Attribute('v', 's', 'a')!=Attribute('v', 's', 'a`'))

class SequenceTests(TestCase):

    def test_eq(self):
        self.assertTrue(Sequence(('a',))==Sequence(('a',)))
        self.assertFalse(Sequence(('a',))==Sequence(('a`',)))

    def test_diff_type(self):
        self.assertFalse((Sequence(('a',))=={}))
        self.assertTrue((Sequence(('a',))!={}))

    def test_ne(self):
        self.assertFalse(Sequence(('a',))!=Sequence(('a',)))
        self.assertTrue(Sequence(('a',))!=Sequence(('a`',)))
    
class APITests(TestCase):

    def setUp(self):
        self.a = API()

    def test_set_and_get(self):
        compare(_marker, self.a.get('foo'))
        compare(None, self.a.get('foo', None))
        compare('default', self.a.get('foo', 'default'))
        self.a.set('foo', 'value')
        compare('value', self.a.get('foo'))

    def test_set_and_get_none(self):
        self.a.set('foo', None)
        compare(None, self.a.get('foo'))

    def test_append_and_get(self):
        self.a.append('foo', 'value1')
        compare(['value1'], self.a.get('foo'))
        self.a.append('foo', 'value2')
        compare(['value1', 'value2'], self.a.get('foo'))
        
    def test_set_append_get(self):
        self.a.set('foo', 'value1')
        with ShouldRaise(ValueError(
            "'foo' is not a sequence, cannot append to it"
            )):
            self.a.append('foo', 'value2')
        compare('value1', self.a.get('foo'))

    def test_append_set_get(self):
        self.a.append('foo', 'value2')
        with ShouldRaise(ValueError(
            "'foo' is a sequence, cannot set it"
            )):
            self.a.set('foo', 'value1')
        compare(['value2'], self.a.get('foo'))

    def test_set_remove_get(self):
        self.a.set('foo', 'value')
        self.a.remove('foo', 'value')
        compare(_marker, self.a.get('foo'))
        compare('default', self.a.get('foo','default'))

    def test_append_remove_get(self):
        self.a.append('foo', 'value1')
        self.a.append('foo', 'value2')
        compare(['value1', 'value2'], self.a.get('foo'))
        self.a.remove('foo', 'value1')
        compare(['value2'], self.a.get('foo'))
    
    def test_append_remove_get_none_value(self):
        self.a.append('foo', None)
        self.a.append('foo', 'value2')
        compare([None, 'value2'], self.a.get('foo'))
        self.a.remove('foo', None)
        compare(['value2'], self.a.get('foo'))
    
    def test_append_remove_all_get(self):
        self.a.append('foo', 'value1')
        self.a.append('foo', 'value2')
        self.a.remove('foo', 'value1')
        self.a.remove('foo', 'value2')
        compare([],self.a.get('foo'))
    
    def test_append_remove_get(self):
        self.a.append('foo', 'value1')
        self.a.append('foo', 'value2')
        self.a.remove('foo')
        compare('default', self.a.get('foo', 'default'))
    
    def test_source_none_specified(self):
        self.a.set('foo', 'bar')
        compare(None, self.a.source('foo'))
    
    def test_set_source_specified(self):
        self.a.set('foo', 'bar', 'line 200 - foo.conf')
        compare('line 200 - foo.conf', self.a.source('foo'))

    def test_set_source_value_supplied(self):
        self.a.set('foo', 'bar', 'line 200 - foo.conf')
        compare('line 200 - foo.conf', self.a.source('foo', 'bar'))

    def test_set_source_none_value_supplied(self):
        self.a.set('foo', None, 'line 200 - foo.conf')
        compare('line 200 - foo.conf', self.a.source('foo', None))

    def test_set_source_wrong_value_supplied(self):
        self.a.set('foo', 'bar', 'line 200 - foo.conf')
        with ShouldRaise(SourceError("'baz' is not current value of 'foo'")):
            self.a.source('foo', 'baz')

    def test_source_sequence(self):
        self.a.append('foo', 'value1', 'line 200 - foo.conf')
        self.a.append('foo', 'value2', 'line 201 - foo.conf')
        # no value, so report where the sequence was
        # first defined
        compare('line 200 - foo.conf', self.a.source('foo'))

    def test_source_sequence_no_first_defined(self):
        self.a.append('foo', 'value1')
        self.a.append('foo', 'value2', 'line 201 - foo.conf')
        # no value, so report where the sequence was
        # first defined, which is None here
        compare(None, self.a.source('foo'))

    def test_source_sequence_value_specified(self):
        self.a.append('foo', 'value1', 'line 200 - foo.conf')
        self.a.append('foo', 'value2', 'line 201 - foo.conf')
        # value specified, so report where that value
        # was defined
        compare('line 201 - foo.conf', self.a.source('foo', 'value2'))

    def test_source_sequence_none_value_specified(self):
        self.a.append('foo', 'value1', 'line 200 - foo.conf')
        self.a.append('foo', None, 'line 201 - foo.conf')
        compare('line 201 - foo.conf', self.a.source('foo', None))

    def test_source_sequence_multiple_identical_values(self):
        self.a.append('foo', 'value1', 'line 200 - foo.conf')
        self.a.append('foo', 'value1', 'line 201 - foo.conf')
        # value specified, so report where that value
        # was first defined
        compare('line 200 - foo.conf', self.a.source('foo', 'value1'))

    def test_source_sequence_wrong_value_specified(self):
        self.a.append('foo', 'value1', 'line 200 - foo.conf')
        self.a.append('foo', 'value2', 'line 201 - foo.conf')
        with ShouldRaise(SourceError("'value3' not found in sequence for 'foo'")):
            self.a.source('foo', 'value3')

    def test_history(self):
        self.a.set('foo', 'bar', 'line 200 - foo.conf')
        self.a.set('foo', 'baz', 'line 201 - baz.conf')
        self.a.set('foo', 'bob', 'line 202 - bob.conf')
        compare([
            C(Attribute,
              value='bob',
              source='line 202 - bob.conf',
              action='set',
              strict=False),
            C(Attribute,
              value='baz',
              source='line 201 - baz.conf',
              action='set',
              strict=False),
            C(Attribute,
              value='bar',
              source='line 200 - foo.conf',
              action='set',
              strict=False),
            ],
            self.a.history('foo')
            )

    def test_history_removed(self):
        self.a.set('foo', 'bar', 'line 200 - foo.conf')
        self.a.remove('foo', 'baz', 'line 201 - baz.conf')
        compare([
            C(Attribute,
              value='baz',
              source='line 201 - baz.conf',
              action='remove',
              strict=False),
            C(Attribute,
              value='bar',
              source='line 200 - foo.conf',
              action='set',
              strict=False),
            ],
            self.a.history('foo')
            )
    
    def test_history_sequence(self):
        # XXX
        return
        self.a.append('foo', 'bar', '1')
        self.a.append('foo', 'baz', '2')
        compare([
            C(Attribute,
              value='bar',
              source='1',
              action='append',
              strict=False),
            ],
            self.a.history('foo')
            )
    
    def test_history_sequence_add_remove(self):
        # XXX
        return
        self.a.append('foo', 'baz', '1')
        self.a.remove('foo', 'baz', '2')
        compare([
            C(Attribute,
              value='bar',
              source='1',
              action='append',
              strict=False),
            ],
            self.a.history('foo')
            )

    def test_history_value(self):
        self.a.set('foo', 'bar', '1')
        self.a.set('foo', 'baz', '2')
        self.a.set('foo', 'bob', '3')
        compare([
            C(Attribute,
              value='bob',
              source='3',
              action='set',
              strict=False),
            C(Attribute,
              value='baz',
              source='2',
              action='set',
              strict=False),
            C(Attribute,
              value='bar',
              source='1',
              action='set',
              strict=False),
            ],
            self.a.history('foo', 'bob')
            )

    def test_history_value_none(self):
        #XXX
        return
        self.a.set('foo', 'bar', '1')
        self.a.set('foo', None, '2')
        compare([
            C(Attribute,
              value=None,
              source='3',
              action='set',
              strict=False),
            C(Attribute,
              value='bar',
              source='1',
              action='set',
              strict=False),
            ],
            self.a.history('foo', None)
            )

    def test_history_value_wrong(self):
        # XXX
        return
        self.a.set('foo', 'bar', '1')
        self.a.set('foo', 'baz', '2')
        self.a.set('foo', 'bob', '3')
        with ShouldRaise():
            self.a.history('foo', 'bar')

    def test_history_sequence_value(self):
        pass

    def test_history_sequence_value_none(self):
        pass

    def test_history_sequence_value_wrong(self):
        pass
    
