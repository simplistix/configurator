import sys

PY2 = sys.version_info.major == 2

if PY2:
    from cStringIO import StringIO
else:
    from io import StringIO
