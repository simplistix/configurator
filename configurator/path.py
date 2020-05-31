class NotPresent(Exception): pass


class Op(object):

    name = 'op'

    def get(self, data):
        raise TypeError('Cannot use %s() in source' % self.name)

    def ensure(self, *args):
        raise TypeError('Cannot use %s() as target' % self.name)

    set = ensure

    def not_present(self, data):
        return data


class ItemOp(Op):

    def __init__(self, text):
        self.text = text

    def get(self, data):
        try:
            return data[self.text]
        except (KeyError, IndexError):
            return NotPresent(self.text)

    def ensure(self, data):
        try:
            return data[self.text]
        except KeyError:
            data[self.text] = value = {}
            return value

    def set(self, data, value, _):
        data[self.text] = value

    def str(self, base):
        return '{}[{!r}]'.format(base, self.text)


class AttrOp(Op):

    def __init__(self, text):
        self.text = text

    def get(self, data):
        return getattr(data, self.text, NotPresent(self.text))

    def ensure(self, data):
        return getattr(data, self.text)

    def set(self, data, value, _):
        setattr(data, self.text, value)

    def str(self, base):
        return '{}.{}'.format(base, self.text)


class TextOp(Op):

    def __init__(self, text):
        self.text = text

    def get(self, data):
        getitem = getattr(data, '__getitem__', None)
        if getitem is None:
            return getattr(data, self.text, NotPresent(self.text))
        else:
            try:
                return getitem(self.text)
            except KeyError:
                return NotPresent(self.text)

    def ensure(self, data):
        getitem = getattr(data, '__getitem__', None)
        if getitem is None:
            return getattr(data, self.text)
        else:
            try:
                return getitem(self.text)
            except KeyError:
                data[self.text] = value = {}
                return value

    def set(self, data, value, _):
        setitem = getattr(data, '__setitem__', None)
        if setitem is None:
            return setattr(data, self.text, value)
        else:
            return setitem(self.text, value)

    def str(self, base):
        if base:
            return base+'.'+self.text
        else:
            return self.text


class ConvertOp(Op):

    name = 'convert'

    def __init__(self, callable_):
        self.callable = callable_

    def get(self, data):
        return self.callable(data)

    def str(self, base):
        callable_str = getattr(self.callable, '__name__', repr(self.callable))
        return '{}({}, {})'.format(self.name, base, callable_str)


class RequiredOp(Op):

    name = 'required'

    def get(self, data):
        return data

    def not_present(self, data):
        raise data

    def str(self, base):
        return '{}({})'.format(self.name, base)


class IfSuppliedOp(Op):

    name = 'if_supplied'

    def __init__(self, false_values):
        self.false_values = false_values

    def get(self, data):
        if data in self.false_values:
            return NotPresent(data)
        return data

    def str(self, base):
        return '{}({})'.format(self.name, base)


class InsertOp(Op):

    name = 'insert'

    def __init__(self, index):
        self.index = index

    def ensure(self, data):
        value = {}
        data.insert(self.index, value)
        return value

    def set(self, data, value, _):
        data.insert(self.index, value)

    def str(self, base):
        return '{}.{}({!r})'.format(base, self.name, self.index)


class AppendOp(Op):

    name = 'append'

    def ensure(self, data):
        value = {}
        data.append(value)
        return value

    def set(self, data, value, _):
        data.append(value)

    def str(self, base):
        return '{}.{}()'.format(base, self.name)


class MergeOp(Op):

    name = 'merge'

    def ensure(self, data):
        raise TypeError('merge() must be final operation')

    def set(self, data, value, context):
        return context.merge(data, value)

    def str(self, base):
        return '{}.{}()'.format(base, self.name)


class ValueOp(Op):

    name = 'value'

    def __init__(self, value):
        self.value = value

    def get(self, data):
        return self.value

    def str(self, base):
        return '{}({!r})'.format(self.name, self.value)


class Path(object):
    """
    A generative object used for constructing source or target mappings.
    See :doc:`mapping` for details.
    """

    def __init__(self, name, *ops):
        self.name = name
        self.ops = ops

    def _extend(self, op):
        return type(self)(self.name, *(self.ops + (op,)))

    def __getitem__(self, name):
        """
        Indicate that the source or target should be traversed by item access.
        """
        return self._extend(ItemOp(name))

    def __getattr__(self, name):
        """
        Indicate that the source or target should be traversed by attribute access.
        """
        return self._extend(AttrOp(name))

    def insert(self, index):
        """
        Indicate that a target should be mapped by inserting at the specified
        index.
        """
        return self._extend(InsertOp(index))

    def append(self):
        """
        Indicate that a target should be mapped by appending.
        """
        return self._extend(AppendOp())

    def merge(self):
        """
        Indicate that a target should be mapped by merging.
        """
        return self._extend(MergeOp())

    def __str__(self):
        str = self.name
        for op in self.ops:
            str = op.str(str)
        return str

    def __repr__(self):
        return 'Path:{}'.format(str(self))


def parse_text(segment):
    if isinstance(segment, str):
        segment = Path('', *(TextOp(part) for part in segment.split('.')))
    elif not isinstance(segment, Path):
        segment = Path('', ItemOp(segment))
    return segment
