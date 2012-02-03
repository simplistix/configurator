# Copyright (c) 2011-2012 Simplistix Ltd
# See license.txt for license details.

from . import _marker
from .exceptions import SourceError

class Attribute:

    def __init__(self, value, source, action, previous=None):
        self.value = value
        self.source = source
        self.action = action
        self.previous = previous

    def __repr__(self):
        return 'A'+repr((self.value, self.source, self.action))

    def __eq__(self,other):
        if not isinstance(other, Attribute):
            return False
        return (
            self.value == other.value and
            self.action == other.action
            )

    def __ne__(self, other):
        return not(self==other)

    def __call__(self, default):
        if self.action != 'remove':
            return self.value
        return default
    
class Sequence(list):

    def __call__(self, default):
        result = []
        for attr in self:
            if attr.action != 'remove':
                result.append(attr.value)
        return result

class API(dict):
    """
    The API for storing configuration information in a
    :class:`~configurator.section.Section` and accessing specific
    details about the information stored.
    """
    # introspection
    
    def source(self, name, value=_marker):
        obj = self[name]
        if isinstance(obj, Sequence):
            if value is _marker and obj:
                value = obj[0].value
            attr = _marker
            for potential_attr in obj:
                if value == potential_attr.value:
                    attr = potential_attr
                    break
            if attr is _marker:
                raise SourceError('%r not found in sequence for %r' % (
                    value, name
                    ))
            return attr.source
        else:
            if value is not _marker and obj.value != value:
                raise SourceError('%r is not current value of %r' % (
                    value, name
                    ))
            return obj.source

    def history(self, name, value=_marker):
        history = []
        attr = self[name]
        while attr:
            history.append(attr)
            attr = attr.previous
        return history

    # modification
    
    def set(self, name, value, source=None):
        previous = super(API, self).get(name)
        if isinstance(previous, Sequence):
            raise ValueError('%r is a sequence, cannot set it' % name)
        self[name] = Attribute(value, source, 'set', previous=previous)

    def append(self, name, value, source=None):
        sequence = super(API, self).get(name)
        if sequence is None:
            self[name] = sequence = Sequence()
        elif not isinstance(sequence, Sequence):
            raise ValueError('%r is not a sequence, cannot append to it' % name)
        sequence.append(Attribute(value, source, 'append'))

    def remove(self, name, value=_marker, source=None):
        current = super(API, self).get(name)
        if isinstance(current, Sequence) and value is not _marker:
            for i, item in enumerate(current):
                if item.value==value:
                    current[i] = Attribute(value, source, 'remove',
                                           previous=item)
        else:
            self[name] = Attribute(value, source, 'remove',
                                   previous=current)

    # access
    
    def get(self, name, default=_marker):
        """
        Get the named attribute from the section this api corresponds
        to. If the section has not such named attribute, the
        default is returned.

        In general, this method should not be used and information
        should be obtained using the methods on the associated
        :class:`~configurator.section.Section`.
        """
        value = dict.get(self, name, _marker)
        if value is _marker:
            return default
        return value(default)


    
