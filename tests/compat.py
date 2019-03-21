import sys

PY2 = sys.version_info.major == 2

def type_error(text):
    if PY2:
        text = text.replace("<class '", "<type '")
    return TypeError(text)
