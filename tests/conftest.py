import pytest
from testfixtures import TempDirectory


@pytest.fixture
def dir():
    with TempDirectory(encoding='ascii') as d:
        yield d
