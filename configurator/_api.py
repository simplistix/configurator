# Copyright (c) 2011-2012 Simplistix Ltd
# See license.txt for license details.

from .exceptions import SourceError
from . import api, marker
from ._utils import get_source

class Attribute:
    """
    A container for the value in a configuration.
    The container records the name the value is associated with, or ``None``
    if there is no name associated with this value.
    It also containts a description of the source the value came from,
    and a string containing the action that caused it to be present
    and the :class:`Attribute` representing the previous value associated
    if there was one.

    If the ``action`` attribute is ``'removed'``, it indicates that this
    value has been removed.
    """

    __slots__ = ('name', 'value', 'action', 'source', 'index', 'previous')
    
    def __init__(self, name, value, action, source, index, previous):
        """
        .. note:: You should never instantiate this class yourself.
        """
        self.name = name
        self.value = value
        self.action = action
        self.source = source
        self.previous = previous
        self.index = index

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
    """

    def __init__(self, section, name, source):
        self.name = name
        self.by_name = dict()
        self.by_order = list()
        self._section = section
        self._source = source or get_source()
        self._history = []
        
    # introspection

    def source(self, name=None):
        """
        Returns the current source location associated with the name
        passed in. If no name is passed, the source location where section
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
        if isinstance(value, API):
            value = value._section
        previous = self.by_name.get(name)
        a = Attribute(name, value, 'set', source or get_source(), 0, previous)
        if previous is None:
            a.index = len(self.by_order)
            self.by_order.append(a)
        else:
            a.index = previous.index
            self.by_order[previous.index] = a
        self.by_name[name] = a
        self._history.append(a)
        # avoid import loop
        from .section import Section
        if isinstance(value, Section):
            api(value).name = name

    def append(self, value, source=None):
        """
        Append a value to the section associated with this api.

        The source location this value came from can also be supplied as a
        string. While this is optional, it is strongly recommended.
        """
        if isinstance(value, API):
            value = value._section
        a = Attribute(
            None, value, 'append',
            source or get_source(),
            len(self.by_order),
            None
            )
        self.by_order.append(a)
        self._history.append(a)

    def remove(self, name=marker, value=marker, source=None):
        """
        Remove a value from the section associated with this api.

        The name the value is associated with or the value itself may be
        passed. If the latter, all occurences of that value within the
        section will be removed.
        """
        source = source or get_source()
        if name is not marker:
            previous = self.by_name.get(name)
            if previous is None or previous.value is not marker:
                a = Attribute(
                    name, marker, 'remove', source, 0, previous
                    )
                if previous is None:
                    a.index = len(self.by_order)
                    self.by_order.append(a)
                else:
                    a.index = previous.index
                    self.by_order[previous.index] = a
                self.by_name[name] = a
                self._history.append(a)
        if value is not marker:
            for i, previous in enumerate(self.by_order):
                if previous.value == value:
                    name = previous.name
                    a = Attribute(
                        name, marker, 'remove', source, previous.index, previous
                        )
                    if name:
                        self.by_name[name] = a
                    self.by_order[i] = a
                    self._history.append(a)

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


    
