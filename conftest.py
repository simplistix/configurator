from doctest import REPORT_NDIFF, ELLIPSIS

import pytest
from pyfakefs.pytest_plugin import fs_module as fs
from sybil import Sybil
from sybil.parsers.doctest import DocTestParser
from sybil.parsers.codeblock import PythonCodeBlockParser
from testfixtures import Replacer, TempDirectory
from testfixtures.sybil import FileParser


@pytest.fixture()
def tempdir(fs):
    with TempDirectory(path='/') as d:
        yield d


@pytest.fixture(scope='module')
def replace():
    with Replacer() as replace:
        yield replace


@pytest.fixture()
def skip_no_yaml():
    pytest.importorskip("yaml")


pytest_collect_file = Sybil(
    parsers=[
        DocTestParser(optionflags=REPORT_NDIFF|ELLIPSIS),
        PythonCodeBlockParser(),
        FileParser('tempdir')
    ],
    pattern='*.rst',
    fixtures=['fs', 'replace', 'tempdir', 'skip_no_yaml'],
).pytest()
