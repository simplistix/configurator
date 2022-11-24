import linecache
import tokenize
from doctest import REPORT_NDIFF, ELLIPSIS

import pytest
from pyfakefs.fake_filesystem_unittest import Patcher
from sybil import Sybil
from sybil.parsers.doctest import DocTestParser
from sybil.parsers.codeblock import PythonCodeBlockParser
from testfixtures import Replacer, TempDirectory
from testfixtures.sybil import FileParser


@pytest.fixture(scope='module')
def fs_state():
    pytest.importorskip("yaml")
    patcher = Patcher(additional_skip_names=['expanduser'])
    patcher.setUp()
    patcher.pause()
    yield patcher
    patcher.tearDown()


@pytest.fixture()
def fs(fs_state):
    # We need our own one to have state across sections in documents.
    fs_state.resume()
    linecache.open = fs_state.original_open
    tokenize._builtin_open = fs_state.original_open
    yield fs_state.fs
    fs_state.pause()


@pytest.fixture()
def tempdir(fs):
    with TempDirectory(path='/') as d:
        yield d


@pytest.fixture(scope='module')
def replace():
    with Replacer() as r:
        yield r.replace


pytest_collect_file = Sybil(
    parsers=[
        DocTestParser(optionflags=REPORT_NDIFF|ELLIPSIS),
        PythonCodeBlockParser(),
        FileParser('tempdir')
    ],
    pattern='*.rst',
    fixtures=['fs', 'replace', 'tempdir'],
).pytest()
