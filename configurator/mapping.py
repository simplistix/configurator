from .path import (
    Path, parse_text, ConvertOp, RequiredOp, NotPresent, IfSuppliedOp, ValueOp
)


def load(data, path):
    path = parse_text(path)
    for op in path.ops:
        if isinstance(data, NotPresent):
            op.not_present(data)
        else:
            data = op.get(data)
    return data


def convert(source, callable_):
    """
    A :doc:`mapping <mapping>` operation that indicates the source value
    should be converted by calling ``callable_`` with the original value
    and then using that result from that point in the mapping operation
    onwards.
    """
    source = parse_text(source)
    return source._extend(ConvertOp(callable_))


def required(source):
    """
    A :doc:`mapping <mapping>` operation that indicates the source value
    is required. If it is not present, the exception that occurred when
    trying to obtain it will be raised.
    """
    source = parse_text(source)
    return source._extend(RequiredOp())


def if_supplied(source, false_values=frozenset((None, '', ))):
    """
    A :doc:`mapping <mapping>` operation that indicates the source value
    should be treated as not present if its value is in the supplied
    list of ``false_values``.
    """
    source = parse_text(source)
    return source._extend(IfSuppliedOp(false_values))


def value(value):
    """
    A :doc:`mapping <mapping>` operation that provides a literal source value.
    """
    return Path('', ValueOp(value))


def store(data, path, value, merge_context=None):
    path = parse_text(path)
    if not path.ops:
        raise TypeError('Cannot store at root')
    stack = [data]
    for op in path.ops[:-1]:
        stack.append(op.ensure(stack[-1]))
    if not isinstance(value, NotPresent):
        data = path.ops[-1].set(stack[-1], value, merge_context)
        if data is not None:
            # uh oh, we have to replace the upstream object:
            if len(stack) < 2:
                stack[0] = data
            else:
                path.ops[-2].set(stack[-2], data, merge_context)
    return stack[0]


source = Path('source')
target = Path('target')
