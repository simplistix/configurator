class NotPresent(Exception): pass


class ItemOp(object):

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
            data[self.text] = value ={}
            return value

    def set(self, data, value, _):
        data[self.text] = value

    def str(self, base):
        return '{}[{!r}]'.format(base, self.text)


class AttrOp(object):

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


class TextOp(object):

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


class ConvertOp(object):

    def __init__(self, callable_):
        self.callable = callable_

    def get(self, data):
        if isinstance(data, NotPresent):
            return data
        return self.callable(data)

    def ensure(self, *args):
        raise TypeError('Cannot use convert() as target')

    set = ensure

    def str(self, base):
        callable_str = getattr(self.callable, '__name__', repr(self.callable))
        return 'convert({}, {})'.format(base, callable_str)


class RequiredOp(object):

    def get(self, data):
        if isinstance(data, NotPresent):
            raise data
        return data

    def ensure(self, *args):
        raise TypeError('Cannot use required() as target')

    set = ensure

    def str(self, base):
        return 'required({})'.format(base)


class InsertOp(object):

    def __init__(self, index):
        self.index = index

    def get(self, data):
        raise TypeError('Cannot use insert() in source')

    def ensure(self, data):
        value = {}
        data.insert(self.index, value)
        return value

    def set(self, data, value, _):
        data.insert(self.index, value)

    def str(self, base):
        return '{}.insert({!r})'.format(base, self.index)


class AppendOp(object):

    def get(self, data):
        raise TypeError('Cannot use append() in source')

    def ensure(self, data):
        value = {}
        data.append(value)
        return value

    def set(self, data, value, _):
        data.append(value)

    def str(self, base):
        return '{}.append()'.format(base)


class MergeOp(object):

    def get(self, data):
        raise TypeError('Cannot use merge() in source')

    def ensure(self, data):
        raise TypeError('merge() must be final operation')

    def set(self, data, value, context):
        return context.merge(data, value)

    def str(self, base):
        return '{}.merge()'.format(base)


class Path(object):

    def __init__(self, name, *ops):
        self.name = name
        self.ops = ops

    def _extend(self, op):
        return type(self)(self.name, *(self.ops + (op,)))

    def __getitem__(self, name):
        return self._extend(ItemOp(name))

    def __getattr__(self, name):
        return self._extend(AttrOp(name))

    def insert(self, index):
        return self._extend(InsertOp(index))

    def append(self):
        return self._extend(AppendOp())

    def merge(self):
        return self._extend(MergeOp())

    def __str__(self):
        str = self.name
        for op in self.ops:
            str = op.str(str)
        return str

    def __repr__(self):
        return 'Path({!r})'.format(self.name)


def parse_text(segment):
    if isinstance(segment, str):
        segment = Path('', *(TextOp(part) for part in segment.split('.')))
    return segment
