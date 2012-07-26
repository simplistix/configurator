# Copyright (c) 2011-2012 Simplistix Ltd
# See license.txt for license details.

from .exceptions import SourceError
from sys import _getframe

from . import api, marker
from ._utils import get_source

class Attribute:
    """
    A container for information about a specific value in a configuration.

    .. attribute:: name

      The name the value is associated with. ``None`` if this value
      has no name to identify it.
      
    .. attribute:: value

      The value. In the case of the of ``removed`` attributes, this
      will be the :obj:`marker`.
      
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
    The API for storing configuration information in a
    :class:`~configurator.section.Section` and accessing specific
    details about the information stored.

    .. note:: You should never instantiate this class yourself.

    """

    def __init__(self, section, name, source):
        self.name = name
        self.by_name = dict()
        self.by_order = list()
        self._section = section
        self._source = source or get_source()
        self._history = []
        
    def __repr__(self):
        return '<API for Section %r at 0x%x>' % (self.name, id(self._section))
    
    def _attribute(self, name, value, source, previous=None):
        # avoid import loop
        from .section import Section
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
            index = previous.index
            self.by_order[previous.index] = a
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


    
