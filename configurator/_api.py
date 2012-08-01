# Copyright (c) 2011-2012 Simplistix Ltd
# See license.txt for license details.

from sys import _getframe

from . import api, marker
from .section import Section
from .exceptions import AlreadyProcessed
from ._utils import get_source

class Attribute:
    """
    A container for information about a specific value in a configuration.

    .. attribute:: name

      The name the value is associated with. ``None`` if this value
      has no name to identify it.
      
    .. attribute:: value

      The value. In the case of the of ``removed`` attributes, this
      will be the :obj:`~configurator.marker`.
      
    .. attribute:: action

      A string containing the name of the :class:`API` method that
      caused this value to be present.
      
    .. attribute:: source

      A string containing the source location that this value came from.
      
    .. attribute:: index

      An implementation detail that should be ignored.
      
    .. attribute:: previous

      An :class:`Attribute` instance representing the previous value
      associated with ``name``. This will be ``None`` if there was no previous
      value.

    .. note:: You should never instantiate this class yourself.
    """

    __slots__ = ('name', 'value', 'action', 'source', 'index', 'previous')

    def __init__(self, name, value, action, source, index, previous):
        self.name = name
        self.value = value
        self.action = action
        self.source = source
        self.index = index
        self.previous = previous

    def __repr__(self):
        return 'Attribute'+repr(tuple(
            (getattr(self, name) for name in self.__slots__)
            ))

    def __str__(self):
        return 'Attribute(%s)' % (', '.join(
            ('%s=%r' % (name, getattr(self, name)) for name in self.__slots__)
            ))

    def __eq__(self,other):
        if not isinstance(other, Attribute):
            return False
        for name in self.__slots__[:-1]:
            if getattr(self, name) != getattr(other, name):
                return False
        return True

    def __ne__(self, other):
        return not(self==other)

    def history(self):
        """
        Returns a sequence of :class:`Attribute` instances representing the
        history of this :class:`Attribute`. The last item in this sequence
        with be the :class:`Attribute` on which this method was called.

        .. note::
        
          History is ordered from oldest to newest, so that the natural
          ordering of a history sequence will be similar to that of a
          traceback.
        """
        history = []
        attr = self
        while attr:
            history.append(attr)
            attr = attr.previous
        history.reverse()
        return history
    
class API(object):
    """
    The API for interacting with configuration information in a
    :class:`~configurator.section.Section`.

    .. note:: You should never instantiate this class yourself.

    .. attribute:: processed

      A boolean attribute recording whether :meth:`processed` has been called on
      this :class:`API`.
    """

    processed = False
    
    def __init__(self, section, name, source):
        self.name = name
        self.by_name = dict()
        self.by_order = list()
        self._section = section
        self._source = source or get_source()
        self._history = []
        self._actions = []
        
    def __repr__(self):
        return '<API for Section %r at 0x%x>' % (self.name, id(self._section))
    
    def _attribute(self, name, value, source, previous=None):
        # avoid import loop
        if isinstance(value, API):
            value = value._section
        if isinstance(value, Section):
            api(value).name = name
        action = _getframe(1).f_code.co_name
        source = source or get_source(3)
        previous = previous or self.by_name.get(name)
        if previous is None:
            index = len(self.by_order)
        else:
            if value is marker and previous.value is marker:
                return
            index = previous.index

        a = Attribute(name, value, action, source, index, previous)
        
        if previous is None:
            self.by_order.append(a)
        else:
            self.by_order[index] = a
        if name is not None:
            self.by_name[name] = a
        self._history.append(a)
        
    # introspection

    def source(self, name=None):
        """
        Returns the current source location associated with the name
        passed in. If no name is passed, the source location where the section
        associated with this API was first defined will be returned.

        If the source location cannot be worked out for any reason,
        ``None`` will be returned.
        """
        if name is None:
            return self._source
        attr = self.by_name.get(name)
        if attr is None or attr.value is marker:
            return None
        return attr.source

    def history(self, name=None):
        """
        Returns a sequence of :class:`Attribute` instances representing the
        history of the item associated with the name passed in. If no name
        is passed in, the history of the entire section will be returned.

        If a name is passed and no value is associated with that name in
        this section, a :class:`KeyError` will be raised.
        If the section is empty and no name is passed, an empty list will
        be returned.

        .. note::
        
          History is ordered from oldest to newest, so that the natural
          ordering of a history sequence will be similar to that of a
          traceback.
        """
        if name is None:
            return self._history
        return self.by_name[name].history()

    # modification
    
    def set(self, name, value, source=None):
        """
        Set the value for the supplied name in the section associated with this
        api to be that supplied.

        The source location this value came from can also be supplied as a
        string. While this is optional, it is strongly recommended.
        """
        self._attribute(name, value, source)

    def replace(self, name, value, source=None):
        """
        This method is identical to :meth:`set` except that values set, when
        merged into another :class:`~configurator.section.Section` using
        :meth:`merge` will always completely replace the value in that section.

        This is particularly useful when ``value`` is a
        :class:`~configurator.section.Section` instance as otherwise its
        contained values would be merged with those in the target section.
        """
        self._attribute(name, value, source)

    def append(self, value, source=None):
        """
        Append a value to the section associated with this api.

        The source location this value came from can also be supplied as a
        string. While this is optional, it is strongly recommended.
        """
        self._attribute(None, value, source)

    def remove(self, name=marker, value=marker, source=None):
        """
        Remove a value from the section associated with this api.

        The name the value is associated with or the value itself may be
        passed. If the latter, all occurences of that value within the
        section will be removed.
        """
        if name is not marker:
            self._attribute(name, marker, source)
        if value is not marker:
            for i, previous in enumerate(self.by_order):
                if previous.value == value:
                    name = previous.name
                    self._attribute(name, marker, source, previous)

    def action(self, callable):
        """
        Add a callable that will be processed when the :meth:`process` method is
        called on this :class:`API`. Callables will be called in the order they
        are actioned and will be called with the :class:`API` instance they were
        actioned on and the :class:`~configurator.section.Section` associated
        with that :class:`API` as parameters.

        The object passed must be a callable with the following signature:

        .. code-block:: python

            def my_action(section, api):
                ...
                
        """
        self._actions.append(callable)
        
    def process(self, strict=True):
        """
        Process all actions associated with attributes in the section this api
        is associated with and recursively through all sub-sections within
        that section.

        Attributes are processed in order and actions are processed in the order
        they were added. For nested sections, attributes in the deepest sections
        are processed first with those associated with the root section
        processed last.

        If a section ends up being processed more than once, an
        :class:`~configurator.exceptions.AlreadyProcessed` exception will be raised
        unless a ``strict`` parameter of ``False`` is passed, in which case
        :class:`Section` instances that have already been processed will be
        ignored.
        """
        if self.processed:
            if strict:
                raise AlreadyProcessed(
                    'Section %r has already been processed' % self.name
                    )
            else:
                return
        for a in self.items():
            if isinstance(a.value, Section):
                api(a.value).process()
        for action in self._actions:
            action(self._section, self)
        self.processed = True
    
    def clone(self):
        """
        Return a clone of the :class:`~configurator.section.Section` associated
        with this :class:`API`. Sub-sections will be cloned but all other values
        will not be copied in any way.

        Furthermore, since :meth:`process` is likely to introduce values that
        should not appear in more than one :class:`~configurator.section.Section`,
        if any section or sub-section has been processed, an
        :class:`AlreadyProcessed` exception will be raised if an attempt is made
        to clone them.
        """
        if self.processed:
            raise AlreadyProcessed(
                    "Can't clone %r as it has been processed" % self.name
                    )
        section = Section(self.name, self._source)
        a = api(section)
        a.by_name = dict(self.by_name)
        a.by_order = list(self.by_order)
        a._history = list(self._history)
        a._actions = list(self._actions)
        for a in self.by_order:
            if isinstance(a.value, Section):
                a.value = api(a.value).clone()
        return section

    # access

    def items(self):
        """
        Return a sequence of :class:`Attribute` instances representing the
        current contents of the section this api corresponds to.
        """
        return [a for a in self.by_order if a.action != 'remove']
    
    def get(self, name, default=marker):
        """
        Get the named :class:`Attribute` from the section this api corresponds
        to. If the section has not such named attribute, the
        default is returned.

        In general, this method should not be used and information
        should be obtained using the methods on the associated
        :class:`~configurator.section.Section`.
        """
        a = self.by_name.get(name, marker)
        if a is marker or a.action=='remove':
            return default
        return a


    
