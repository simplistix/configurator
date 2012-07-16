# Copyright (c) 2012 Simplistix Ltd
# See license.txt for license details.

from sys import _getframe

def get_source(level=2):
    frame = _getframe(level)
    code = frame.f_code
    return 'File %r, line %s, in %s' % (
        code.co_filename,
        frame.f_lineno,
        code.co_name,
        )
