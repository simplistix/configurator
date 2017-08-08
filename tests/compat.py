from configurator.compat import PY2

def type_error(text):
    if PY2:
        text = text.replace("<class '", "<type '")
    return TypeError(text)
