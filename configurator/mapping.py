class ItemOp(object):

    def __init__(self, text):
        self.text = text

    def get(self, data):
        return data[self.text]

    def ensure(self, data):
        try:
            return data[self.text]
        except KeyError:
            data[self.text] = value ={}
            return value

    def set(self, data, value, _):
        data[self.text] = value


class AttrOp(object):

    def __init__(self, text):
        self.text = text

    def get(self, data):
        return getattr(data, self.text)

    ensure = get

    def set(self, data, value, _):
        setattr(data, self.text, value)


class TextOp(object):

    def __init__(self, text):
        self.text = text

    def get(self, data):
        getitem = getattr(data, '__getitem__', None)
        if getitem is None:
            return getattr(data, self.text)
        else:
            return getitem(self.text)

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


class ConvertOp(object):

    def __init__(self, callable_):
        self.callable = callable_

    def get(self, data):
        return self.callable(data)

    def ensure(self, *args):
        raise TypeError('Cannot use convert() as target')

    set = ensure


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


class AppendOp(object):

    def get(self, data):
        raise TypeError('Cannot use append() in source')

    def ensure(self, data):
        value = {}
        data.append(value)
        return value

    def set(self, data, value, _):
        data.append(value)


class MergeOp(object):

    def get(self, data):
        raise TypeError('Cannot use merge() in source')

    def ensure(self, data):
        raise TypeError('merge() must be final operation')

    def set(self, data, value, context):
        return context.merge(data, value)


class Path(object):

    def __init__(self, *ops):
        self.ops = ops

    def _extend(self, op):
        return type(self)(*(self.ops + (op,)))

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


def parse_text(segment):
    if isinstance(segment, str):
        segment = Path(*(TextOp(part) for part in segment.split('.')))
    return segment


def load(data, path):
    path = parse_text(path)
    for op in path.ops:
        data = op.get(data)
    return data


def convert(source, callable_):
    source = parse_text(source)
    return source._extend(ConvertOp(callable_))


def store(data, path, value, merge_context=None):
    path = parse_text(path)
    if not path.ops:
        raise TypeError('Cannot store at root')
    stack = [data]
    for op in path.ops[:-1]:
        stack.append(op.ensure(stack[-1]))
    data = path.ops[-1].set(stack[-1], value, merge_context)
    if data is not None:
        # uh oh, we have to replace the upstream object:
        if len(stack) < 2:
            stack[0] = data
        else:
            path.ops[-2].set(stack[-2], data, merge_context)
    return stack[0]


source = target = Path()
