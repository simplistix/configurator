import linecache
import tokenize
from doctest import REPORT_NDIFF, ELLIPSIS

import pytest
from pyfakefs.fake_filesystem_unittest import Patcher
from sybil import Sybil
from sybil.parsers.doctest import DocTestParser, FIX_BYTE_UNICODE_REPR
from sybil.parsers.codeblock import CodeBlockParser
from testfixtures import Replacer


@pytest.fixture(scope='module')
def fs():
    pytest.importorskip("yaml")
    # We need our own one to have it be module scoped.
    patcher = Patcher()
    patcher.setUp()
    linecache.open = patcher.original_open
    tokenize._builtin_open = patcher.original_open
    yield patcher.fs
    patcher.tearDown()


@pytest.fixture(scope='module')
def replace():
    with Replacer() as r:
        yield r.replace


pytest_collect_file = Sybil(
    parsers=[
        DocTestParser(optionflags=REPORT_NDIFF|ELLIPSIS|FIX_BYTE_UNICODE_REPR),
        CodeBlockParser(['print_function']),
    ],
    pattern='*.rst',
    fixtures=['fs'],
).pytest()
