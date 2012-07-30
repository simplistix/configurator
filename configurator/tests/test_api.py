# Copyright (c) 2011-2012 Simplistix Ltd
# See license.txt for license details.

from configurator import api, marker
from configurator._api import API, Attribute
from configurator.exceptions import AlreadyProcessed
from configurator.section import Section
from unittest import TestCase
from testfixtures import compare, ShouldRaise

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
        
class APITests(SourceMixin, TestCase):

    def setUp(self):
        super(APITests, self).setUp()
        self.section = object()
        self.a = API(self.section, 'the name', None)

    called_with = False
    
    def _action(self, *args):
        self.called_with = args
            
    def test_repr(self):
        compare("<API for Section 'the name' at 0x%x>" % id(self.section),
                repr(self.a))

    def test_str(self):
        compare("<API for Section 'the name' at 0x%x>" % id(self.section),
                str(self.a))
    
    # set tests
    
    def test_set_get_simple(self):
        # before
        compare(marker, self.a.get('foo'))
        compare(None, self.a.get('foo', None))
        compare('default', self.a.get('foo', 'default'))
        compare([], self.a.items())
        # set
        self.a.set('foo', 'value')
        # after
        compare(Attribute('foo', 'value', 'set', 'default_source3', 0, None),
                self.a.get('foo'))
        compare([Attribute('foo', 'value', 'set', 'default_source3', 0, None)],
                self.a.items())
        compare('default_source3',
                self.a.source(name='foo'))
        compare([Attribute('foo', 'value', 'set', 'default_source3', 0, None)],
                self.a.history(name='foo'))
        compare([Attribute('foo', 'value', 'set', 'default_source3', 0, None)],
                self.a.history())

    def test_set_get_none_value(self):
        # set
        self.a.set('foo', None)
        # after
        compare(Attribute('foo', None, 'set', 'default_source3', 0, None),
                self.a.get('foo'))
        compare([Attribute('foo', None, 'set', 'default_source3', 0, None)],
                self.a.items())
        compare('default_source3',
                self.a.source(name='foo'))
        compare([Attribute('foo', None, 'set', 'default_source3', 0, None)],
                self.a.history(name='foo'))
        compare([Attribute('foo', None, 'set', 'default_source3', 0, None)],
                self.a.history())

    def test_set_update_existing(self):
        # set
        self.a.set('foo', 'v1', 's1')
        self.a.set('foo', 'v2', 's2')
        # after
        compare(Attribute('foo', 'v2', 'set', 's2', 0, None),
                self.a.get('foo'))
        compare([Attribute('foo', 'v2', 'set', 's2', 0, None)],
                self.a.items())
        compare('s2',
                self.a.source('foo'))
        compare([
            Attribute('foo', 'v1', 'set', 's1', 0, None),
            Attribute('foo', 'v2', 'set', 's2', 0, None),
            ], self.a.history('foo'))
        compare([
            Attribute('foo', 'v1', 'set', 's1', 0, None),
            Attribute('foo', 'v2', 'set', 's2', 0, None),
            ], self.a.history())

    def test_set_set_indexes(self):
        self.a.set('foo', 'v1', 's1')
        self.a.set('bar', 'v2', 's2')
        compare([Attribute('foo', 'v1', 'set', 's1', 0, None),
                 Attribute('bar', 'v2', 'set', 's2', 1, None)],
                self.a.items())

    def test_set_section(self):
        s = Section()
        self.a.set('foo', s)
        self.assertTrue(self.a.get('foo').value is s)

    def test_set_api(self):
        s = Section()
        a = api(s)
        self.a.set('foo', a)
        self.assertTrue(self.a.get('foo').value is s)
        
    def test_set_section_name(self):
        s = Section()
        self.a.set('foo', s)
        compare('foo', api(s).name)

    # append tests
    
    def test_append(self):
        # append
        self.a.append('v1')
        # after
        items = self.a.items()
        compare([Attribute(None, 'v1', 'append', 'default_source3', 0, None)],
                items)
        compare('default_source3',
                items[0].source)
        compare([
            Attribute(None, 'v1', 'append', 'default_source3', 0, None),
            ], items[0].history())
        compare([
            Attribute(None, 'v1', 'append', 'default_source3', 0, None),
            ], self.a.history())
        
    def test_append_append(self):
        # append
        self.a.append('v1', 's1')
        self.a.append('v2', 's2')
        # after
        items = self.a.items()
        compare([
            Attribute(None, 'v1', 'append', 's1', 0, None),
            Attribute(None, 'v2', 'append', 's2', 1, None)
            ], items)
        compare('s1',
                items[0].source)
        compare('s2',
                items[1].source)
        compare([
            Attribute(None, 'v1', 'append', 's1', 0, None),
            ], items[0].history())
        compare([
            Attribute(None, 'v2', 'append', 's2', 1, None),
            ], items[1].history())
        compare([
            Attribute(None, 'v1', 'append', 's1', 0, None),
            Attribute(None, 'v2', 'append', 's2', 1, None)
            ], self.a.history())
        
    def test_append_section(self):
        expected = Section()
        self.a.append(expected)
        actual = tuple(self.a.items())[0].value
        self.assertTrue(expected is actual)

    def test_append_api(self):
        expected = Section()
        a = api(expected)
        self.a.append(a)
        actual = tuple(self.a.items())[0].value
        self.assertTrue(expected is actual)
        
    def test_append_section_name(self):
        s = Section()
        self.a.append(s)
        compare(None, api(s).name)

    # remove tests

    def test_remove_name(self):
        # setup
        self.a.set('foo', 'v1', 's1')
        # remove
        self.a.remove('foo')
        # check
        compare('default', self.a.get('foo', 'default'))
        compare([],
                self.a.items())
        compare(None,
                self.a.source(name='foo'))
        compare([
            Attribute('foo', 'v1', 'set', 's1', 0, None),
            Attribute('foo', marker, 'remove', 'default_source3', 0, None)
            ], self.a.history(name='foo'))
        compare([
            Attribute('foo', 'v1', 'set', 's1', 0, None),
            Attribute('foo', marker, 'remove', 'default_source3', 0, None)
            ], self.a.history())

    def test_remove_name_not_present(self):
        # we record the remove, handy for merging Sections
        # remove
        self.a.remove('foo')
        # check
        compare([],
                self.a.items())
        compare(None,
                self.a.source(name='foo'))
        compare([
            Attribute('foo', marker, 'remove', 'default_source3', 0, None)
            ], self.a.history(name='foo'))
        compare([
            Attribute('foo', marker, 'remove', 'default_source3', 0, None)
            ], self.a.history())

    def test_remove_value(self):
        # check that remove by identity works
        value = object()
        self.a.set('foo', value)
        # remove
        self.a.remove(value=value)
        # check
        compare('default', self.a.get('foo', 'default'))
        compare([],
                self.a.items())
        compare(None,
                self.a.source(name='foo'))
        compare([
            Attribute('foo', value, 'set', 'default_source3', 0, None),
            Attribute('foo', marker, 'remove', 'default_source3', 0, None)
            ], self.a.history(name='foo'))
        compare([
            Attribute('foo', value, 'set', 'default_source3', 0, None),
            Attribute('foo', marker, 'remove', 'default_source3', 0, None)
            ], self.a.history())

    def test_remove_by_name_previous_remove(self):
        # setup
        self.a.set('foo', 'v1')
        self.a.set('bar', 'v2')
        # do removes
        self.a.remove(value='v1')
        self.a.remove(name='bar')
        # check (especially history)
        compare('default', self.a.get('foo', 'default'))
        compare('default', self.a.get('bar', 'default'))
        compare([],
                self.a.items())
        compare(None,
                self.a.source(name='foo'))
        compare(None,
                self.a.source(name='bar'))
        compare([
            Attribute('foo', 'v1', 'set', 'default_source3', 0, None),
            Attribute('foo', marker, 'remove', 'default_source3', 0, None)
            ], self.a.history(name='foo'))
        compare([
            Attribute('bar', 'v2', 'set', 'default_source3', 1, None),
            Attribute('bar', marker, 'remove', 'default_source3', 1, None)
            ], self.a.history(name='bar'))
        compare([
            Attribute('foo', 'v1', 'set', 'default_source3', 0, None),
            Attribute('bar', 'v2', 'set', 'default_source3', 1, None),
            Attribute('foo', marker, 'remove', 'default_source3', 0, None),
            Attribute('bar', marker, 'remove', 'default_source3', 1, None),
            ], self.a.history())

    def test_remove_nothing_specified(self):
        # just does nothing
        self.a.remove()
        compare([],
                self.a.items())
        compare([
            ], self.a.history())

    def test_double_remove_by_name(self):
        # setup
        self.a.set('foo', 'v1')
        # do removes
        self.a.remove(name='foo')
        self.a.remove(name='foo')
        # check (especially history)
        compare('default', self.a.get('foo', 'default'))
        compare([],
                self.a.items())
        compare(None,
                self.a.source(name='foo'))
        compare([
            Attribute('foo', 'v1', 'set', 'default_source3', 0, None),
            Attribute('foo', marker, 'remove', 'default_source3', 0, None)
            ], self.a.history(name='foo'))
        compare([
            Attribute('foo', 'v1', 'set', 'default_source3', 0, None),
            Attribute('foo', marker, 'remove', 'default_source3', 0, None),
            ], self.a.history())

    def test_double_remove_by_value(self):
        # setup
        self.a.set('foo', 'v1')
        # do removes
        self.a.remove(value='v1')
        self.a.remove(value='v1')
        # check (especially history)
        compare('default', self.a.get('foo', 'default'))
        compare([],
                self.a.items())
        compare(None,
                self.a.source(name='foo'))
        compare([
            Attribute('foo', 'v1', 'set', 'default_source3', 0, None),
            Attribute('foo', marker, 'remove', 'default_source3', 0, None)
            ], self.a.history(name='foo'))
        compare([
            Attribute('foo', 'v1', 'set', 'default_source3', 0, None),
            Attribute('foo', marker, 'remove', 'default_source3', 0, None),
            ], self.a.history())
    
    def test_remove_value_multiple_match(self):
        self.a.set('foo', 'v', 's1')
        self.a.set('bar', 'v', 's2')
        # remove
        self.a.remove(value='v', source='s3')
        # check
        compare('default', self.a.get('foo', 'default'))
        compare('default', self.a.get('bar', 'default'))
        compare([],
                self.a.items())
        compare(None,
                self.a.source(name='foo'))
        compare(None,
                self.a.source(name='bar'))
        compare([
            Attribute('foo', 'v', 'set', 's1', 0, None),
            Attribute('foo', marker, 'remove', 's3', 0, None)
            ], self.a.history(name='foo'))
        compare([
            Attribute('bar', 'v', 'set', 's2', 1, None),
            Attribute('bar', marker, 'remove', 's3', 1, None)
            ], self.a.history(name='bar'))
        compare([
            Attribute('foo', 'v', 'set', 's1', 0, None),
            Attribute('bar', 'v', 'set', 's2', 1, None),
            Attribute('foo', marker, 'remove', 's3', 0, None),
            Attribute('bar', marker, 'remove', 's3', 1, None)
            ], self.a.history())

    def test_add_append_remove(self):
        self.a.set('foo', 'v', 's1')
        self.a.append('v', 's2')
        # remove
        self.a.remove(value='v', source='s3')
        # check
        compare('default', self.a.get('foo', 'default'))
        compare([],
                self.a.items())
        compare(None,
                self.a.source(name='foo'))
        compare([
            Attribute('foo', 'v', 'set', 's1', 0, None),
            Attribute('foo', marker, 'remove', 's3', 0, None)
            ], self.a.history(name='foo'))
        compare([
            Attribute('foo', 'v', 'set', 's1', 0, None),
            Attribute(None, 'v', 'append', 's2', 1, None),
            Attribute('foo', marker, 'remove', 's3', 0, None),
            Attribute(None, marker, 'remove', 's3', 1, None)
            ], self.a.history())
    
    # combined operation tests
    def test_set_set_append_set_append_remove(self):
        # a good mix of stuff to exercise history
        # (all with sources)
        self.a.set('foo', 'v1', 's1')
        self.a.set('bar', 'v2', 's2')
        self.a.append('v3', 's3')
        self.a.set('bar', 'v4', 's4')
        self.a.append('v5', 's5')
        self.a.remove(value='v2', source='s6') # should do nothing
        self.a.remove(name='foo', source='s7')
        # check
        compare('default', self.a.get('foo', 'default'))
        compare(Attribute('bar', 'v4', 'set', 's4', 1, None),
                self.a.get('bar', 'default'))
        compare([
            Attribute('bar', 'v4', 'set', 's4', 1, None),
            Attribute(None, 'v3', 'append', 's3', 2, None),
            Attribute(None, 'v5', 'append', 's5', 3, None),
            ], self.a.items())
        compare(None,
                self.a.source(name='foo'))
        compare('s4',
                self.a.source(name='bar'))
        compare([
            Attribute('foo', 'v1', 'set', 's1', 0, None),
            Attribute('foo', marker, 'remove', 's7', 0, None)
            ], self.a.history(name='foo'))
        compare([
            Attribute('bar', 'v2', 'set', 's2', 1, None),
            Attribute('bar', 'v4', 'set', 's4', 1, None),
            ], self.a.history(name='bar'))
        compare([
            Attribute('foo', 'v1', 'set', 's1', 0, None),
            Attribute('bar', 'v2', 'set', 's2', 1, None),
            Attribute(None, 'v3', 'append', 's3', 2, None),
            Attribute('bar', 'v4', 'set', 's4', 1, None),
            Attribute(None, 'v5', 'append', 's5', 3, None),
            Attribute('foo', marker, 'remove', 's7', 0, None),
            ], self.a.history())
    
    # source-only tests

    def test_source_set_remove_by_name(self):
        self.a.set('foo', 'v', 's1')
        # remove
        self.a.remove(name='foo', source='s3')
        # check
        compare('default', self.a.get('foo', 'default'))
        compare([],
                self.a.items())
        compare(None,
                self.a.source(name='foo'))
        compare([
            Attribute('foo', 'v', 'set', 's1', 0, None),
            Attribute('foo', marker, 'remove', 's3', 0, None)
            ], self.a.history(name='foo'))
        compare([
            Attribute('foo', 'v', 'set', 's1', 0, None),
            Attribute('foo', marker, 'remove', 's3', 0, None),
            ], self.a.history())
        
    def test_source_section(self):
        compare('source', API(None, None, 'source').source())
        
    def test_source_section_empty(self):
        compare('default_source', self.a.source())
        
    def test_source_name_not_present(self):
        compare(None, self.a.source('foo'))

    def test_source_none_specified(self):
        self.a.set('foo', 'bar')
        compare('default_source3', self.a.source('foo'))
    
    def test_set_source_specified(self):
        self.a.set('foo', 'bar', 'line 200 - foo.conf')
        compare('line 200 - foo.conf', self.a.source('foo'))

    # history only tests
    
    def test_history_name_not_present(self):
        with ShouldRaise(KeyError('foo')):
            self.a.history('foo')

    def test_history_empty_section(self):
        compare([], self.a.history())

    # process tests
    
    def test_process_empty(self):
        self.a.process()
        compare(True, self.a.processed)

    def test_process_simple(self):
        self.a.action(self._action)
        self.a.process()
        compare(True, self.a.processed)
        compare(self.called_with, (self.section, self.a))
            
    def test_process_order(self):
        call_order = []
        def action1(section, api):
            call_order.append('action1')
        def action2(section, api):
            call_order.append('action2')
        self.a.action(action1)
        self.a.action(action2)
        self.a.process()
        compare(True, self.a.processed)
        compare(['action1', 'action2'], call_order)
        
    def test_process_tree(self):
        call_order = []
        def action(section, api):
            call_order.append(api.get('index').value)
        a = [self.a]
        self.a.set('index', 0)
        self.a.action(action)
        for i in range(1, 8):
            si = Section()
            ai = api(si)
            ai.set('index', i)
            a.append(ai)
            ai.action(action)
            
        self.a.set('a1', a[1])
        a[1].set('a2', a[2])
        a[1].set('a3', a[3])
        self.a.set('a4', a[4])
        a[4].set('a5', a[5])
        a[5].set('a6', a[6])
        a[4].set('a7', a[7])

        self.a.process()
        
        # test leaf-first node traversal
        compare([2, 3, 1, 6, 5, 7, 4, 0], call_order)

        # test all sections are processed
        for ai in a:
            compare(True, ai.processed)

    def test_reprocess_strict(self):
        self.a.action(self._action)
        self.a.process()
        self.called_with = False
        with ShouldRaise(AlreadyProcessed(
            "Section 'the name' has already been processed"
            )):
            self.a.process()
        self.assertFalse(self.called_with)
    
    def test_reprocess_non_strict(self):
        self.a.action(self._action)
        self.a.process()
        self.called_with = False
        self.a.process(strict=False)
        self.assertFalse(self.called_with)

    # clone tests
    def test_clone_simple(self):
        # stuff that should be cloned
        self.a._source = 'foo'
        self.a.set('x', 1)
        self.a.set('y', 1)
        self.a.set('y', 2)
        self.a.remove('z')
        def foo(): pass
        self.a.action(foo)
        s_ = self.a.clone()
        self.assertTrue(isinstance(s_, Section))
        self.assertFalse(s_ is self.section)
        
        a_ = api(s_)
        self.assertFalse(a_.processed)
        
        compare(self.a.name, a_.name)
        compare(self.a.source(), a_.source())
        compare(self.a.by_name, a_.by_name)
        self.assertFalse(self.a.by_name is a_.by_name)
        compare(self.a.by_order, a_.by_order)
        self.assertFalse(self.a.by_order is a_.by_order)
        compare(self.a.history(), a_.history())
        self.assertFalse(self.a._history is a_._history)
        compare(self.a._actions, a_._actions)
        self.assertFalse(self.a._actions is a_._actions)

    def test_clone_nested(self):
        s1 = Section()
        s1.x = 1
        s2 = Section()
        s2.y = 2
        a2 = api(s2)
        self.a.set('s1', s1)
        self.a.set('s2', a2)

        s_ = self.a.clone()

        compare(api(s_.s1).history(), api(s1).history())
        compare(api(s_.s2).history(), api(s2).history())

        self.assertFalse(s_.s1 is s1)
        self.assertFalse(s_.s2 is s2)
    
    def test_clone_already_processed(self):
        self.a.process()
        with ShouldRaise(AlreadyProcessed(
            "Can't clone 'the name' as it has been processed"
            )):
            self.a.clone()
                         

        s = Section()
