from .path import Path, parse_text, ConvertOp, RequiredOp, NotPresent


def load(data, path):
    path = parse_text(path)
    for op in path.ops:
        data = op.get(data)
    return data


def convert(source, callable_):
    source = parse_text(source)
    return source._extend(ConvertOp(callable_))


def required(source):
    source = parse_text(source)
    return source._extend(RequiredOp())


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
